from __future__ import annotations

import httpx

from dhlkit import DhlAPIError, DhlNotFoundError, DhlRateLimitError


def test_error_parses_problem_detail() -> None:
    response = httpx.Response(
        401,
        json={"status": 401, "title": "Unauthorized", "detail": "Bad credentials"},
        headers={"correlation-id": "request-1"},
    )

    error = DhlAPIError.from_response(response)

    assert str(error) == "Bad credentials"
    assert error.status_code == 401
    assert error.title == "Unauthorized"
    assert error.request_id == "request-1"


def test_error_uses_status_subclasses() -> None:
    assert isinstance(DhlAPIError.from_response(httpx.Response(404)), DhlNotFoundError)
    assert isinstance(DhlAPIError.from_response(httpx.Response(429)), DhlRateLimitError)
