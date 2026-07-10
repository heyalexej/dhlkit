from __future__ import annotations

import base64

import httpx

from dhlkit.config import DhlConfig


class BasicKeySecretAuth:
    """Legacy tracking gateway auth: developer key/secret, not GKP credentials."""

    refreshes_on_401 = False

    def __init__(self, config: DhlConfig) -> None:
        self._config = config

    def _headers(self) -> dict[str, str]:
        api_key = self._config.require_api_key()
        api_secret = self._config.require_api_secret()
        encoded = base64.b64encode(f"{api_key}:{api_secret}".encode()).decode("ascii")
        return {
            "Authorization": f"Basic {encoded}",
            "DHL-API-Key": api_key,
        }

    def headers(self, client: httpx.Client) -> dict[str, str]:
        return self._headers()

    async def headers_async(self, client: httpx.AsyncClient) -> dict[str, str]:
        return self._headers()

    def invalidate(self) -> None:
        return None
