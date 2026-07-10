from __future__ import annotations

from collections.abc import Callable, Mapping
from types import TracebackType
from typing import Any, Self

import httpx

from .auth import (
    ApiKeyHeaderAuth,
    AuthStrategy,
    BasicKeySecretAuth,
    FileTokenCache,
    RopcBearerAuth,
    TokenCache,
)
from .config import DhlConfig
from .resources import (
    AsyncPickupResource,
    AsyncPostnumberResource,
    AsyncTrackingResource,
    PickupResource,
    PostnumberResource,
    TrackingResource,
)
from .resources.tracking_legacy import AsyncLegacyTrackingResource, LegacyTrackingResource
from .resources.tracking_unified import AsyncUnifiedTrackingResource, UnifiedTrackingResource
from .transport import AsyncDhlTransport, DhlTransport


class DhlClient:
    """Synchronous entry point with authentication selected per resource."""

    def __init__(
        self,
        config: DhlConfig | None = None,
        *,
        http_client: httpx.Client | None = None,
        token_cache: TokenCache | None = None,
    ) -> None:
        self.config = config or DhlConfig.from_env()
        self._owns_http_client = http_client is None
        self._http_client = http_client or httpx.Client(
            timeout=httpx.Timeout(self.config.timeout),
        )
        self._transport = DhlTransport(self.config, self._http_client)

        bearer = RopcBearerAuth(self.config, token_cache or FileTokenCache())
        legacy_auth = BasicKeySecretAuth(self.config)
        unified_auth = ApiKeyHeaderAuth(self.config)
        self.pickup = PickupResource(self, bearer, self.config.pickup_url)
        self.postnumber = PostnumberResource(self, bearer, self.config.postnumber_url)
        self.tracking = TrackingResource(
            LegacyTrackingResource(
                self,
                legacy_auth,
                self.config.legacy_tracking_url,
                self.config,
            ),
            UnifiedTrackingResource(self, unified_auth, self.config.unified_tracking_url),
        )

    def _request(
        self,
        *,
        auth: AuthStrategy,
        base_url: str,
        operation: str,
        method: str,
        path: str,
        path_params: Mapping[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        body: Any = None,
        response_model: Any = None,
        response_parser: Callable[[bytes], Any] | None = None,
        accepted_statuses: set[int] | None = None,
    ) -> Any:
        return self._transport.request(
            auth=auth,
            base_url=base_url,
            operation=operation,
            method=method,
            path=path,
            path_params=path_params,
            params=params,
            headers=headers,
            body=body,
            response_model=response_model,
            response_parser=response_parser,
            accepted_statuses=accepted_statuses,
        )

    def close(self) -> None:
        if self._owns_http_client:
            self._http_client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


class AsyncDhlClient:
    """Asynchronous entry point with the same per-resource authentication model."""

    def __init__(
        self,
        config: DhlConfig | None = None,
        *,
        http_client: httpx.AsyncClient | None = None,
        token_cache: TokenCache | None = None,
    ) -> None:
        self.config = config or DhlConfig.from_env()
        self._owns_http_client = http_client is None
        self._http_client = http_client or httpx.AsyncClient(
            timeout=httpx.Timeout(self.config.timeout),
        )
        self._transport = AsyncDhlTransport(self.config, self._http_client)

        bearer = RopcBearerAuth(self.config, token_cache or FileTokenCache())
        legacy_auth = BasicKeySecretAuth(self.config)
        unified_auth = ApiKeyHeaderAuth(self.config)
        self.pickup = AsyncPickupResource(self, bearer, self.config.pickup_url)
        self.postnumber = AsyncPostnumberResource(self, bearer, self.config.postnumber_url)
        self.tracking = AsyncTrackingResource(
            AsyncLegacyTrackingResource(
                self,
                legacy_auth,
                self.config.legacy_tracking_url,
                self.config,
            ),
            AsyncUnifiedTrackingResource(self, unified_auth, self.config.unified_tracking_url),
        )

    async def _request(
        self,
        *,
        auth: AuthStrategy,
        base_url: str,
        operation: str,
        method: str,
        path: str,
        path_params: Mapping[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        body: Any = None,
        response_model: Any = None,
        response_parser: Callable[[bytes], Any] | None = None,
        accepted_statuses: set[int] | None = None,
    ) -> Any:
        return await self._transport.request(
            auth=auth,
            base_url=base_url,
            operation=operation,
            method=method,
            path=path,
            path_params=path_params,
            params=params,
            headers=headers,
            body=body,
            response_model=response_model,
            response_parser=response_parser,
            accepted_statuses=accepted_statuses,
        )

    async def aclose(self) -> None:
        if self._owns_http_client:
            await self._http_client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()
