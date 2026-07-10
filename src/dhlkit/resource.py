from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from .auth.base import AuthStrategy


class Resource:
    base_url: str

    def __init__(self, client: Any, auth: AuthStrategy, base_url: str) -> None:
        self._client = client
        self._auth = auth
        self.base_url = base_url

    def _request(
        self,
        operation: str,
        method: str,
        path: str,
        *,
        path_params: Mapping[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        body: Any = None,
        response_model: Any = None,
        response_parser: Callable[[bytes], Any] | None = None,
        accepted_statuses: set[int] | None = None,
    ) -> Any:
        return self._client._request(
            auth=self._auth,
            base_url=self.base_url,
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


class AsyncResource:
    base_url: str

    def __init__(self, client: Any, auth: AuthStrategy, base_url: str) -> None:
        self._client = client
        self._auth = auth
        self.base_url = base_url

    async def _request(
        self,
        operation: str,
        method: str,
        path: str,
        *,
        path_params: Mapping[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        body: Any = None,
        response_model: Any = None,
        response_parser: Callable[[bytes], Any] | None = None,
        accepted_statuses: set[int] | None = None,
    ) -> Any:
        return await self._client._request(
            auth=self._auth,
            base_url=self.base_url,
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
