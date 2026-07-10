from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from .errors import DhlConfigError

DEFAULT_TIMEOUT = 30.0


class DhlConfig(BaseSettings):
    """Credentials and transport settings for DHL Parcel DE.

    Values are read from ``DHL_*`` environment variables and an optional local
    ``.env``. Use :meth:`from_file` for the protected XDG JSON credential file.
    """

    model_config = SettingsConfigDict(
        env_prefix="DHL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_key: SecretStr | None = None
    api_secret: SecretStr | None = None
    gkp_user: SecretStr | None = None
    gkp_password: SecretStr | None = None
    sandbox: bool = False
    timeout: float = Field(default=DEFAULT_TIMEOUT, gt=0)
    max_retries: int = Field(default=2, ge=0)
    retry_backoff: float = Field(default=0.5, ge=0)
    retry_max_backoff: float = Field(default=30.0, ge=0)
    base_url: str | None = None

    @classmethod
    def from_env(cls) -> DhlConfig:
        """Load ``DHL_*`` variables and a repository-local, ignored ``.env``."""
        return cls()

    @classmethod
    def from_file(cls, path: str | Path | None = None) -> DhlConfig:
        """Load a mode-0600 JSON file from the XDG config directory by default."""
        config_path = Path(path).expanduser() if path is not None else _default_config_path()
        if not config_path.is_file():
            raise DhlConfigError(f"DHL config file does not exist: {config_path}")
        if os.name != "nt" and config_path.stat().st_mode & 0o077:
            raise DhlConfigError(f"DHL config file must have mode 0600: {config_path}")
        try:
            payload: Any = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise DhlConfigError(f"Could not read DHL config file {config_path}: {exc}") from exc
        if not isinstance(payload, dict):
            raise DhlConfigError(f"DHL config file must contain a JSON object: {config_path}")
        unknown = set(payload) - set(cls.model_fields)
        if unknown:
            names = ", ".join(sorted(unknown))
            raise DhlConfigError(f"Unknown DHL config field(s): {names}")
        return cls.model_validate(payload)

    @property
    def token_url(self) -> str:
        return f"{self._api_root}/parcel/de/account/auth/ropc/v1/token"

    @property
    def pickup_url(self) -> str:
        return f"{self._api_root}/parcel/de/transportation/pickup/v3"

    @property
    def postnumber_url(self) -> str:
        return f"{self._api_root}/parcel/de/account/postnumber/v1"

    @property
    def legacy_tracking_url(self) -> str:
        root = self.base_url.rstrip("/") if self.base_url else "https://api-eu.dhl.com"
        return f"{root}/parcel/de/tracking/v0"

    @property
    def unified_tracking_url(self) -> str:
        if self.base_url:
            root = self.base_url.rstrip("/")
        else:
            root = "https://api-test.dhl.com" if self.sandbox else "https://api-eu.dhl.com"
        return f"{root}/track"

    @property
    def _api_root(self) -> str:
        if self.base_url:
            return self.base_url.rstrip("/")
        return "https://api-sandbox.dhl.com" if self.sandbox else "https://api-eu.dhl.com"

    def require_api_key(self) -> str:
        return self._required_secret("api_key", self.api_key)

    def require_api_secret(self) -> str:
        return self._required_secret("api_secret", self.api_secret)

    def require_gkp_user(self) -> str:
        return self._required_secret("gkp_user", self.gkp_user)

    def require_gkp_password(self) -> str:
        return self._required_secret("gkp_password", self.gkp_password)

    @staticmethod
    def _required_secret(name: str, value: SecretStr | None) -> str:
        if value is None or not value.get_secret_value():
            env_name = f"DHL_{name.upper()}"
            raise DhlConfigError(f"Missing {env_name}")
        return value.get_secret_value()


def _default_config_path() -> Path:
    explicit = os.getenv("DHLKIT_CONFIG")
    if explicit:
        return Path(explicit).expanduser()
    root = Path(os.getenv("XDG_CONFIG_HOME", "~/.config")).expanduser()
    return root / "dhlkit" / "config.json"


def default_token_cache_path() -> Path:
    root = Path(os.getenv("XDG_CACHE_HOME", "~/.cache")).expanduser()
    return root / "dhlkit" / "tokens.json"
