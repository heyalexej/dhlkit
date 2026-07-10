from __future__ import annotations

from typing import Protocol

import httpx


class AuthStrategy(Protocol):
    """Authentication attached to one DHL resource, never to the whole client."""

    refreshes_on_401: bool

    def headers(self, client: httpx.Client) -> dict[str, str]: ...

    async def headers_async(self, client: httpx.AsyncClient) -> dict[str, str]: ...

    def invalidate(self) -> None: ...
