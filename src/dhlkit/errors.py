from __future__ import annotations

from typing import Any

import httpx
import orjson


class DhlError(Exception):
    """Base exception for dhlkit failures."""


class DhlConfigError(DhlError):
    """Raised when credentials or local configuration are unusable."""


class DhlTransportError(DhlError):
    """Raised when no HTTP response could be obtained."""


class DhlAuthError(DhlError):
    """Raised when DHL token acquisition fails."""


class DhlAPIError(DhlError):
    """A non-success response returned by a DHL resource."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        title: str | None = None,
        detail: str | None = None,
        response: httpx.Response | None = None,
        payload: Any = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.title = title
        self.detail = detail
        self.response = response
        self.payload = payload
        self.request_id = request_id

    @classmethod
    def from_response(cls, response: httpx.Response) -> DhlAPIError:
        try:
            payload: Any = orjson.loads(response.content)
        except orjson.JSONDecodeError:
            payload = response.text

        title = detail = None
        if isinstance(payload, dict):
            title = _string_or_none(payload.get("title"))
            detail = _string_or_none(payload.get("detail") or payload.get("message"))
        message = (
            detail or title or response.reason_phrase or f"DHL returned HTTP {response.status_code}"
        )
        error_type: type[DhlAPIError]
        if response.status_code == 429:
            error_type = DhlRateLimitError
        elif response.status_code == 404:
            error_type = DhlNotFoundError
        else:
            error_type = cls
        return error_type(
            message,
            status_code=response.status_code,
            title=title,
            detail=detail,
            response=response,
            payload=payload,
            request_id=response.headers.get("correlation-id")
            or response.headers.get("x-correlation-id")
            or response.headers.get("x-request-id"),
        )


class DhlRateLimitError(DhlAPIError):
    """Raised for HTTP 429 responses."""


class DhlNotFoundError(DhlAPIError):
    """Raised for HTTP 404 responses."""


def _string_or_none(value: Any) -> str | None:
    return str(value) if value is not None else None
