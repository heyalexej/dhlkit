from __future__ import annotations

from dhlkit.generated.models.tracking_unified import TrackingShipments
from dhlkit.resources.tracking_legacy import LegacyTrackingResult
from dhlkit.unified import _from_legacy, _from_unified


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


def test_live_fixture_sanitizer_removes_embedded_tracking_ids() -> None:
    from record_live_fixtures import _safe_text

    source = "Track at https://carrier.example/parcel/XY123456789ZZ for XY123456789ZZ"

    sanitized = _safe_text(source)

    assert sanitized is not None
    assert "XY123456789ZZ" not in sanitized
    assert "https://carrier.example" not in sanitized
    assert "SANITIZED-ID" in sanitized
