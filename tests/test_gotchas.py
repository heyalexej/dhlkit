from __future__ import annotations

import base64
import json
from typing import Any

import httpx

from dhlkit import DhlClient, InMemoryTokenCache
from dhlkit.auth import RopcBearerAuth


def test_postnumber_uses_post_not_get(config, fixture_bytes, token_response) -> None:
    """Regression for docs/AUTH.md; POST→200 while GET→401, verified 2026-07-09."""
    resource_methods: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/token"):
            return token_response("bearer-token")
        resource_methods.append(request.method)
        return httpx.Response(
            200,
            content=fixture_bytes("postnumber.json"),
            headers={"content-type": "application/json"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        dhl = DhlClient(config, http_client=http_client, token_cache=InMemoryTokenCache())
        result = dhl.postnumber.verify("871902603", firstname="Max", lastname="Mustermann")

    assert result.valid is True
    assert resource_methods == ["POST"]


def test_legacy_tracking_basic_is_key_secret(config, fixture_bytes) -> None:
    """Regression for docs/AUTH.md; Basic is app key/secret, verified 2026-07-09."""
    seen: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen
        seen = request
        return httpx.Response(
            200,
            content=fixture_bytes("tracking_legacy_single.xml"),
            headers={"content-type": "application/xml"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        dhl = DhlClient(config, http_client=http_client, token_cache=InMemoryTokenCache())
        dhl.tracking.legacy("00340434780401935407")

    assert seen is not None
    encoded = seen.headers["Authorization"].removeprefix("Basic ")
    assert base64.b64decode(encoded).decode() == "test-api-key:test-api-secret"
    assert base64.b64decode(encoded).decode() != "test-gkp-user:test-gkp-password"


def test_legacy_tracking_gkp_creds_in_xml(config, fixture_bytes) -> None:
    """Regression for docs/AUTH.md; GKP credentials belong only in XML, verified 2026-07-09."""
    seen: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen
        seen = request
        return httpx.Response(
            200,
            content=fixture_bytes("tracking_legacy_single.xml"),
            headers={"content-type": "application/xml"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        dhl = DhlClient(config, http_client=http_client, token_cache=InMemoryTokenCache())
        dhl.tracking.legacy("00340434780401935407")

    assert seen is not None
    xml = seen.url.params["xml"]
    assert 'appname="test-gkp-user"' in xml
    assert 'password="test-gkp-password"' in xml
    assert "test-gkp-user" not in seen.headers["Authorization"]
    assert seen.headers["DHL-API-Key"] == "test-api-key"


def test_pickup_location_type_id_and_asid(config, token_response) -> None:
    """Regression for docs/AUTH.md; location is type=Id + asId, verified 2026-07-09."""
    payload: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal payload
        if request.url.path.endswith("/token"):
            return token_response("bearer-token")
        payload = json.loads(request.content)
        return httpx.Response(200, json={})

    order = {
        "customerDetails": {"billingNumber": "123456789012AB"},
        "pickupLocation": {"id": "AS1234567890"},
        "pickupDetails": {"pickupDate": {"type": "ASAP"}},
        "shipmentDetails": {"shipments": [{"transportationType": "PAKET"}]},
    }
    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        dhl = DhlClient(config, http_client=http_client, token_cache=InMemoryTokenCache())
        dhl.pickup.create(order)

    assert payload["pickupLocation"] == {"type": "Id", "asId": "AS1234567890"}
    assert "id" not in payload["pickupLocation"]


def test_unified_apikey_header_lowercase(config, fixture_bytes) -> None:
    """Regression for docs/AUTH.md; exact header spelling verified 2026-07-09."""
    raw_names: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        raw_names.extend(name for name, _value in request.headers.raw)
        return httpx.Response(
            200,
            content=fixture_bytes("tracking_unified.json"),
            headers={"content-type": "application/json"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        dhl = DhlClient(config, http_client=http_client, token_cache=InMemoryTokenCache())
        dhl.tracking.unified("00340434780401935407")

    assert b"dhl-api-key" in raw_names
    assert b"DHL-API-Key" not in raw_names


def test_no_bearer_and_apikey_together(config, fixture_bytes, token_response) -> None:
    """Regression for docs/AUTH.md; gateway requires one auth scheme, verified 2026-07-09."""
    resource_headers: httpx.Headers | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal resource_headers
        if request.url.path.endswith("/token"):
            return token_response("bearer-token")
        resource_headers = request.headers
        return httpx.Response(
            200,
            content=fixture_bytes("pickup_locations.json"),
            headers={"content-type": "application/json"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        dhl = DhlClient(config, http_client=http_client, token_cache=InMemoryTokenCache())
        dhl.pickup.locations()

    assert resource_headers is not None
    assert resource_headers["Authorization"] == "Bearer bearer-token"
    assert "dhl-api-key" not in resource_headers


def test_ropc_token_reused_until_expiry(config, token_response) -> None:
    """Regression for docs/AUTH.md; token TTL reuse was verified 2026-07-09."""
    now = [0.0]
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return token_response(f"token-{calls}")

    auth = RopcBearerAuth(config, InMemoryTokenCache(), clock=lambda: now[0])
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert auth.headers(client)["Authorization"] == "Bearer token-1"
        assert auth.headers(client)["Authorization"] == "Bearer token-1"
        now[0] = 1771.0
        assert auth.headers(client)["Authorization"] == "Bearer token-2"

    assert calls == 2


def test_tracking_legacy_single_event_is_list(config, fixture_bytes) -> None:
    """Regression for docs/AUTH.md; one and many XML events are lists, verified 2026-07-09."""
    fixture_names = iter(("tracking_legacy_single.xml", "tracking_legacy_multiple.xml"))

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=fixture_bytes(next(fixture_names)),
            headers={"content-type": "application/xml"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        dhl = DhlClient(config, http_client=http_client, token_cache=InMemoryTokenCache())
        single = dhl.tracking.legacy("00340434780401935407")
        multiple = dhl.tracking.legacy("00340434780401935407")

    assert isinstance(single.shipments[0].events, list)
    assert len(single.shipments[0].events) == 1
    assert isinstance(multiple.shipments[0].events, list)
    assert len(multiple.shipments[0].events) == 2


def test_legacy_tracking_live_nested_events_are_preserved(fixture_bytes) -> None:
    """Regression for live v0 nesting; portal and production shapes differ, verified 2026-07-10."""
    from dhlkit.resources.tracking_legacy import _parse_response

    result = _parse_response(fixture_bytes("tracking_legacy_return.xml"))

    assert len(result.shipments) == 1
    assert len(result.shipments[0].events) == 13
    assert result.shipments[0].returned is True
    assert any(event.ice == "RETRN" for event in result.shipments[0].events)
