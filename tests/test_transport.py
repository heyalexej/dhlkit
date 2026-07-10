from __future__ import annotations

import httpx

from dhlkit import DhlClient, InMemoryTokenCache


def test_bearer_refreshes_once_on_401(config, fixture_bytes) -> None:
    token_calls = 0
    resource_tokens: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal token_calls
        if request.url.path.endswith("/token"):
            token_calls += 1
            return httpx.Response(
                200,
                json={
                    "access_token": f"token-{token_calls}",
                    "token_type": "Bearer",
                    "expires_in": 1800,
                },
            )
        resource_tokens.append(request.headers["Authorization"])
        if request.headers["Authorization"] == "Bearer token-1":
            return httpx.Response(401, json={"title": "Unauthorized"})
        return httpx.Response(
            200,
            content=fixture_bytes("pickup_locations.json"),
            headers={"content-type": "application/json"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        dhl = DhlClient(config, http_client=http_client, token_cache=InMemoryTokenCache())
        result = dhl.pickup.locations()

    assert len(result) == 1
    assert token_calls == 2
    assert resource_tokens == ["Bearer token-1", "Bearer token-2"]


def test_idempotent_request_retries_transient_status(config, fixture_bytes) -> None:
    config = config.model_copy(update={"max_retries": 1, "retry_backoff": 0})
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(503)
        return httpx.Response(
            200,
            content=fixture_bytes("tracking_unified.json"),
            headers={"content-type": "application/json"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        dhl = DhlClient(config, http_client=http_client, token_cache=InMemoryTokenCache())
        result = dhl.tracking.unified("00340434780401935407")

    assert result.shipments
    assert calls == 2


def test_injected_http_client_remains_open(config, fixture_bytes) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=fixture_bytes("tracking_unified.json"),
            headers={"content-type": "application/json"},
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    dhl = DhlClient(config, http_client=http_client, token_cache=InMemoryTokenCache())

    dhl.close()

    assert not http_client.is_closed
    http_client.close()
