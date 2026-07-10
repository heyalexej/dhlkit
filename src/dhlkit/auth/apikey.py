from __future__ import annotations

import httpx

from dhlkit.config import DhlConfig


class ApiKeyHeaderAuth:
    """Unified Tracking auth using only the lowercase ``dhl-api-key`` header."""

    refreshes_on_401 = False

    def __init__(self, config: DhlConfig) -> None:
        self._config = config

    def headers(self, client: httpx.Client) -> dict[str, str]:
        return {"dhl-api-key": self._config.require_api_key()}

    async def headers_async(self, client: httpx.AsyncClient) -> dict[str, str]:
        return {"dhl-api-key": self._config.require_api_key()}

    def invalidate(self) -> None:
        return None
