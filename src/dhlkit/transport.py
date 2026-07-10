from __future__ import annotations

import logging as stdlib_logging
import time
from collections.abc import Callable, Mapping
from functools import cache
from typing import Any
from urllib.parse import quote

import httpx
import orjson
import structlog
from pydantic import BaseModel, TypeAdapter

from .auth.base import AuthStrategy
from .config import DhlConfig
from .errors import DhlAPIError, DhlTransportError
from .logging import redact_secrets
from .retry import run_with_retry, run_with_retry_async

logger = structlog.wrap_logger(
    stdlib_logging.getLogger("dhlkit.transport"),
    processors=[redact_secrets, structlog.stdlib.render_to_log_kwargs],
    wrapper_class=structlog.stdlib.BoundLogger,
)


class DhlTransport:
    def __init__(self, config: DhlConfig, client: httpx.Client) -> None:
        self.config = config
        self.client = client

    def request(
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
        url = _url(base_url, path, path_params)
        refreshed = False

        def send() -> httpx.Response:
            nonlocal refreshed
            request = self._build_request(
                auth=auth,
                method=method,
                url=url,
                params=params,
                headers=headers,
                body=body,
            )
            started = time.monotonic()
            response = self.client.send(request)
            if response.status_code == 401 and auth.refreshes_on_401 and not refreshed:
                response.close()
                auth.invalidate()
                refreshed = True
                request = self._build_request(
                    auth=auth,
                    method=method,
                    url=url,
                    params=params,
                    headers=headers,
                    body=body,
                )
                response = self.client.send(request)
            _log_response(operation, request, response, started)
            return response

        try:
            response = run_with_retry(send, method=method, config=self.config)
        except httpx.HTTPError as exc:
            raise DhlTransportError(f"{operation} transport failure: {exc}") from exc
        return _handle_response(
            response,
            response_model=response_model,
            response_parser=response_parser,
            accepted_statuses=accepted_statuses,
        )

    def _build_request(
        self,
        *,
        auth: AuthStrategy,
        method: str,
        url: str,
        params: Mapping[str, Any] | None,
        headers: Mapping[str, str] | None,
        body: Any,
    ) -> httpx.Request:
        request_headers = {"Accept": "application/json"}
        request_headers.update(auth.headers(self.client))
        request_headers.update(headers or {})
        body_kwargs = _body_kwargs(body)
        return self.client.build_request(
            method,
            url,
            params=_compact(params),
            headers=request_headers,
            timeout=self.config.timeout,
            **body_kwargs,
        )


class AsyncDhlTransport:
    def __init__(self, config: DhlConfig, client: httpx.AsyncClient) -> None:
        self.config = config
        self.client = client

    async def request(
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
        url = _url(base_url, path, path_params)
        refreshed = False

        async def send() -> httpx.Response:
            nonlocal refreshed
            request = await self._build_request(
                auth=auth,
                method=method,
                url=url,
                params=params,
                headers=headers,
                body=body,
            )
            started = time.monotonic()
            response = await self.client.send(request)
            if response.status_code == 401 and auth.refreshes_on_401 and not refreshed:
                await response.aclose()
                auth.invalidate()
                refreshed = True
                request = await self._build_request(
                    auth=auth,
                    method=method,
                    url=url,
                    params=params,
                    headers=headers,
                    body=body,
                )
                response = await self.client.send(request)
            _log_response(operation, request, response, started)
            return response

        try:
            response = await run_with_retry_async(send, method=method, config=self.config)
        except httpx.HTTPError as exc:
            raise DhlTransportError(f"{operation} transport failure: {exc}") from exc
        return _handle_response(
            response,
            response_model=response_model,
            response_parser=response_parser,
            accepted_statuses=accepted_statuses,
        )

    async def _build_request(
        self,
        *,
        auth: AuthStrategy,
        method: str,
        url: str,
        params: Mapping[str, Any] | None,
        headers: Mapping[str, str] | None,
        body: Any,
    ) -> httpx.Request:
        request_headers = {"Accept": "application/json"}
        request_headers.update(await auth.headers_async(self.client))
        request_headers.update(headers or {})
        body_kwargs = _body_kwargs(body)
        return self.client.build_request(
            method,
            url,
            params=_compact(params),
            headers=request_headers,
            timeout=self.config.timeout,
            **body_kwargs,
        )


def _url(base_url: str, path: str, path_params: Mapping[str, Any] | None) -> str:
    rendered = path
    for key, value in (path_params or {}).items():
        rendered = rendered.replace("{" + key + "}", quote(str(value), safe=""))
    return f"{base_url.rstrip('/')}/{rendered.lstrip('/')}"


def _compact(values: Mapping[str, Any] | None) -> dict[str, Any]:
    return {key: value for key, value in (values or {}).items() if value is not None}


def _body_kwargs(body: Any) -> dict[str, Any]:
    if body is None:
        return {}
    if isinstance(body, BaseModel):
        return {"json": body.model_dump(by_alias=True, exclude_none=True)}
    return {"json": body}


def _handle_response(
    response: httpx.Response,
    *,
    response_model: Any,
    response_parser: Callable[[bytes], Any] | None,
    accepted_statuses: set[int] | None,
) -> Any:
    success = (
        response.status_code in accepted_statuses if accepted_statuses else response.is_success
    )
    if not success:
        raise DhlAPIError.from_response(response)
    if response.status_code == 204 or not response.content:
        return None
    if response_parser is not None:
        return response_parser(response.content)
    content_type = response.headers.get("content-type", "")
    if "json" not in content_type:
        return response.content
    payload = orjson.loads(response.content)
    if response_model is None:
        return payload
    return _adapter(response_model).validate_python(payload)


@cache
def _adapter(response_model: Any) -> TypeAdapter[Any]:
    # Compiling a TypeAdapter builds a validator; reuse one per response type
    # instead of rebuilding it on every response.
    return TypeAdapter(response_model)


def _log_response(
    operation: str,
    request: httpx.Request,
    response: httpx.Response,
    started: float,
) -> None:
    logger.debug(
        "http_response",
        operation=operation,
        method=request.method,
        host=request.url.host,
        path=request.url.path,
        status=response.status_code,
        elapsed_ms=int((time.monotonic() - started) * 1000),
    )
