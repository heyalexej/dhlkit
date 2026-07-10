from __future__ import annotations

import json
import os
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from dhlkit.config import default_token_cache_path


@dataclass(frozen=True, repr=False)
class CachedToken:
    access_token: str
    expires_at: float

    def __repr__(self) -> str:
        return f"CachedToken(access_token=<redacted>, expires_at={self.expires_at!r})"


class TokenCache(Protocol):
    """Storage contract used by :class:`RopcBearerAuth`."""

    def get(self, key: str) -> CachedToken | None: ...

    def set(self, key: str, token: CachedToken) -> None: ...

    def clear(self, key: str) -> None: ...


class InMemoryTokenCache:
    """Thread-safe, process-local token cache, useful for short-lived jobs and tests."""

    def __init__(self) -> None:
        self._tokens: dict[str, CachedToken] = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> CachedToken | None:
        with self._lock:
            return self._tokens.get(key)

    def set(self, key: str, token: CachedToken) -> None:
        with self._lock:
            self._tokens[key] = token

    def clear(self, key: str) -> None:
        with self._lock:
            self._tokens.pop(key, None)


class FileTokenCache:
    """Atomic mode-0600 token cache in ``$XDG_CACHE_HOME/dhlkit``."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path).expanduser() if path is not None else default_token_cache_path()
        self._lock = threading.RLock()

    def get(self, key: str) -> CachedToken | None:
        with self._lock:
            payload = self._read()
            item = payload.get(key)
            if not isinstance(item, dict):
                return None
            access_token = item.get("access_token")
            expires_at = item.get("expires_at")
            if not isinstance(access_token, str) or not isinstance(expires_at, int | float):
                return None
            return CachedToken(access_token=access_token, expires_at=float(expires_at))

    def set(self, key: str, token: CachedToken) -> None:
        with self._lock:
            payload = self._read()
            payload[key] = {
                "access_token": token.access_token,
                "expires_at": token.expires_at,
            }
            self._write(payload)

    def clear(self, key: str) -> None:
        with self._lock:
            payload = self._read()
            if key in payload:
                del payload[key]
                self._write(payload)

    def _read(self) -> dict[str, object]:
        if not self.path.exists():
            return {}
        try:
            if os.name != "nt" and self.path.stat().st_mode & 0o077:
                self.path.chmod(0o600)
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def _write(self, payload: dict[str, object]) -> None:
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=".tokens-",
                delete=False,
            ) as handle:
                temporary_path = Path(handle.name)
                json.dump(payload, handle, separators=(",", ":"), sort_keys=True)
                handle.flush()
                os.fsync(handle.fileno())
            temporary_path.chmod(0o600)
            os.replace(temporary_path, self.path)
            self.path.chmod(0o600)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
