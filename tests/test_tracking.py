from __future__ import annotations

import httpx
import pytest

from dhlkit import AsyncDhlClient, DhlClient, InMemoryTokenCache
from dhlkit.errors import DhlAPIError
from dhlkit.generated.models.tracking_unified import TrackingShipments
from dhlkit.resources.tracking import _from_legacy, _from_unified
from dhlkit.resources.tracking_legacy import LegacyTrackingResult


def test_normalizes_unified_fixture(fixture_bytes) -> None:
    source = TrackingShipments.model_validate_json(fixture_bytes("tracking_unified.json"))

    result = _from_unified(source, "fallback")

    assert result.source == "unified"
    assert result.status_code == "transit"
    assert result.events[-1].location == "Bonn"


def test_normalizes_legacy_fixture(fixture_bytes) -> None:
    from dhlkit.resources.tracking_legacy import _parse_response

    source: LegacyTrackingResult = _parse_response(fixture_bytes("tracking_legacy_single.xml"))

    result = _from_legacy(source, "fallback")

    assert result is not None
    assert result.source == "legacy"
    assert result.status_code == "AA"
    assert len(result.events) == 1


def test_real_shape_return_fixture_is_typed_and_sanitized(fixture_bytes) -> None:
    raw = fixture_bytes("tracking_unified_return.json")
    source = TrackingShipments.model_validate_json(raw)
    assert source.shipments is not None

    shipment = source.shipments[0]

    assert shipment.return_flag is not None
    assert shipment.return_flag.root is True
    assert len(shipment.events or []) == 13
    assert any(event.status_detailed == "RETRN_CNCNR_ZN" for event in shipment.events or [])
    assert b"@" not in raw
    assert b'"receiver"' not in raw
    assert b'"sender"' not in raw
    assert b'"streetAddress"' not in raw
    assert b'"postalCode"' not in raw

    normalized = _from_unified(source, "fallback")
    assert normalized.returned is True


def test_parse_response_raises_on_request_level_error() -> None:
    from dhlkit.resources.tracking_legacy import _parse_response

    body = b'<?xml version="1.0" encoding="UTF-8"?><data name="error" code="400" error-status="1"/>'

    with pytest.raises(DhlAPIError):
        _parse_response(body)


def test_track_prefer_legacy_reraises_error_without_calling_unified(config) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if "/tracking/v0/" in request.url.path:
            return httpx.Response(
                200,
                content=b'<data name="error" code="400" error-status="1"/>',
                headers={"content-type": "application/xml"},
            )
        raise AssertionError("unified must not be called when fallback is disabled")

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        dhl = DhlClient(config, http_client=http_client, token_cache=InMemoryTokenCache())
        with pytest.raises(DhlAPIError):
            dhl.tracking.track("00340434780401935407", prefer="legacy", fallback=False)


def test_track_prefer_legacy_falls_back_to_unified_on_error(config, fixture_bytes) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if "/tracking/v0/" in request.url.path:
            return httpx.Response(
                200,
                content=b'<data name="error" code="400"/>',
                headers={"content-type": "application/xml"},
            )
        return httpx.Response(
            200,
            content=fixture_bytes("tracking_unified.json"),
            headers={"content-type": "application/json"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        dhl = DhlClient(config, http_client=http_client, token_cache=InMemoryTokenCache())
        result = dhl.tracking.track("00340434780401935407", prefer="legacy", fallback=True)

    assert result.source == "unified"


@pytest.mark.anyio
async def test_async_track_prefers_legacy_without_calling_unified(config, fixture_bytes) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if "/tracking/v0/" in request.url.path:
            return httpx.Response(
                200,
                content=fixture_bytes("tracking_legacy_single.xml"),
                headers={"content-type": "application/xml"},
            )
        raise AssertionError("unified must not be called when legacy succeeds")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        dhl = AsyncDhlClient(config, http_client=http_client, token_cache=InMemoryTokenCache())
        result = await dhl.tracking.track("00340434780401935407", prefer="legacy")

    assert result.source == "legacy"
    assert result.status_code == "AA"


def test_live_fixture_sanitizer_removes_embedded_tracking_ids() -> None:
    from record_live_fixtures import _safe_text

    source = "Track at https://carrier.example/parcel/XY123456789ZZ for XY123456789ZZ"

    sanitized = _safe_text(source)

    assert sanitized is not None
    assert "XY123456789ZZ" not in sanitized
    assert "https://carrier.example" not in sanitized
    assert "SANITIZED-ID" in sanitized
