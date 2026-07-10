from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import Any

_SECRET_KEY_PARTS = ("api_key", "apikey", "secret", "password", "authorization", "token")


def mask_secret(value: Any) -> str:
    """Return a useful presence indicator without revealing a credential."""
    text = str(value)
    prefix = text[:4] if text else ""
    return f"{prefix}…(len={len(text)})"


def redact_secrets(
    _logger: Any,
    _method_name: str,
    event_dict: MutableMapping[str, Any],
    /,
) -> MutableMapping[str, Any]:
    """structlog processor that recursively masks security-sensitive values."""
    return _redact_mapping(event_dict)


def _redact_mapping(values: Mapping[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in values.items():
        normalized = key.lower().replace("-", "_")
        if any(part in normalized for part in _SECRET_KEY_PARTS):
            redacted[key] = mask_secret(value)
        elif isinstance(value, Mapping):
            redacted[key] = _redact_mapping(value)
        elif isinstance(value, list | tuple):
            redacted[key] = [
                _redact_mapping(item) if isinstance(item, Mapping) else item for item in value
            ]
        else:
            redacted[key] = value
    return redacted
