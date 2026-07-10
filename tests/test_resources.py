from __future__ import annotations

import json

import httpx
import pytest

from dhlkit import AsyncDhlClient, DhlClient, InMemoryTokenCache
from dhlkit.generated.models.pickup import PickupOrder


def _token_response() -> httpx.Response:
    return httpx.Response(
        200,
        json={"access_token": "token", "token_type": "Bearer", "expires_in": 1800},
    )


def test_pickup_create_from_model_sends_expected_wire_body(config) -> None:
    sent: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/token"):
            return _token_response()
        nonlocal sent
        sent = json.loads(request.content)
        return httpx.Response(200, json={})

    order = PickupOrder.model_validate(
        {
            "customerDetails": {"billingNumber": "123456789012AB"},
            "pickupLocation": {"type": "Id", "asId": "AS1234567890"},
            "pickupDetails": {"pickupDate": {"type": "ASAP"}},
            "shipmentDetails": {"shipments": [{"transportationType": "PAKET"}]},
        }
    )
    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        dhl = DhlClient(config, http_client=http_client, token_cache=InMemoryTokenCache())
        dhl.pickup.create(order)

    assert sent["pickupLocation"] == {"type": "Id", "asId": "AS1234567890"}
    assert sent["customerDetails"]["billingNumber"] == "123456789012AB"
    assert sent["shipmentDetails"]["shipments"] == [{"transportationType": "PAKET"}]


def test_pickup_locations_are_typed(config, fixture_bytes) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/token"):
            return _token_response()
        assert request.url.params["postalCode"] == "53113"
        return httpx.Response(
            200,
            content=fixture_bytes("pickup_locations.json"),
            headers={"content-type": "application/json"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        dhl = DhlClient(config, http_client=http_client, token_cache=InMemoryTokenCache())
        locations = dhl.pickup.locations(postal_code="53113")

    assert locations[0].id is not None
    assert locations[0].id.root == "AS1234567890"
    assert locations[0].pickup_address is not None
    assert locations[0].pickup_address.city.root == "Bonn"


def test_postnumber_412_is_typed_negative_result(config) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/token"):
            return _token_response()
        return httpx.Response(412, json={"valid": False})

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        dhl = DhlClient(config, http_client=http_client, token_cache=InMemoryTokenCache())
        result = dhl.postnumber.verify("871902603", firstname="Max", lastname="Mustermann")

    assert result.valid is False


def test_unified_tracking_query_is_typed(config, fixture_bytes) -> None:
    seen: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen
        seen = request
        return httpx.Response(
            200,
            content=fixture_bytes("tracking_unified.json"),
            headers={"content-type": "application/json"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        dhl = DhlClient(config, http_client=http_client, token_cache=InMemoryTokenCache())
        result = dhl.tracking.unified(
            "00340434780401935407",
            language="de",
            recipient_postal_code="53113",
        )

    assert seen is not None
    assert seen.url.params["service"] == "parcel-de"
    assert seen.url.params["language"] == "de"
    shipments = result.shipments
    assert shipments is not None
    status = shipments[0].status
    assert status is not None
    assert status.status_code.root == "transit"


def test_pickup_get_requires_selector(config) -> None:
    transport = httpx.MockTransport(lambda _request: httpx.Response(500))
    with httpx.Client(transport=transport) as client:
        dhl = DhlClient(config, http_client=client, token_cache=InMemoryTokenCache())
        with pytest.raises(ValueError, match="order_id or pickup_date"):
            dhl.pickup.get()


def test_legacy_limits_batch_size(config) -> None:
    transport = httpx.MockTransport(lambda _request: httpx.Response(500))
    with httpx.Client(transport=transport) as client:
        dhl = DhlClient(config, http_client=client, token_cache=InMemoryTokenCache())
        with pytest.raises(ValueError, match="between 1 and 15"):
            dhl.tracking._legacy.track([str(index) for index in range(16)])


@pytest.mark.anyio
async def test_async_postnumber(config, fixture_bytes) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/token"):
            return _token_response()
        return httpx.Response(
            200,
            content=fixture_bytes("postnumber.json"),
            headers={"content-type": "application/json"},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        dhl = AsyncDhlClient(
            config,
            http_client=http_client,
            token_cache=InMemoryTokenCache(),
        )
        result = await dhl.postnumber.verify(
            "871902603",
            firstname="Max",
            lastname="Mustermann",
        )

    assert result.valid is True
