from __future__ import annotations

from typing import Literal

from .client import DhlClient
from .errors import DhlError
from .generated.models.tracking_unified import TrackingShipment, TrackingShipments
from .models import DhlModel
from .resources.tracking_legacy import LegacyShipment, LegacyTrackingResult


class TrackingEvent(DhlModel):
    timestamp: str | None = None
    status: str | None = None
    description: str | None = None
    location: str | None = None


class TrackingResult(DhlModel):
    tracking_number: str
    source: Literal["legacy", "unified"]
    status_code: str | None = None
    status: str | None = None
    description: str | None = None
    timestamp: str | None = None
    delivered: bool = False
    returned: bool = False
    events: list[TrackingEvent]


def track(
    client: DhlClient,
    tracking_number: str,
    *,
    prefer: Literal["legacy", "unified"] = "legacy",
    fallback: bool = True,
) -> TrackingResult:
    """Return one normalized shipment, preferring legacy's higher Parcel DE quota."""
    if prefer == "unified":
        try:
            return _from_unified(client.tracking.unified(tracking_number), tracking_number)
        except DhlError:
            if not fallback:
                raise
            legacy = _from_legacy(client.tracking.legacy(tracking_number), tracking_number)
            return legacy or TrackingResult(
                tracking_number=tracking_number,
                source="legacy",
                events=[],
            )
    try:
        result = _from_legacy(client.tracking.legacy(tracking_number), tracking_number)
        if result is not None:
            return result
    except DhlError:
        if not fallback:
            raise
    return _from_unified(client.tracking.unified(tracking_number), tracking_number)


def _from_legacy(result: LegacyTrackingResult, tracking_number: str) -> TrackingResult | None:
    if not result.shipments:
        return None
    shipment = result.shipments[0]
    return _legacy_shipment(shipment, tracking_number)


def _legacy_shipment(shipment: LegacyShipment, fallback_number: str) -> TrackingResult:
    latest = shipment.events[-1] if shipment.events else None
    return TrackingResult(
        tracking_number=shipment.piece_code or shipment.searched_piece_code or fallback_number,
        source="legacy",
        status_code=latest.standard_event_code if latest else None,
        status=shipment.short_status or shipment.status,
        description=shipment.status,
        timestamp=shipment.status_timestamp,
        delivered=shipment.delivered,
        returned=shipment.returned,
        events=[
            TrackingEvent(
                timestamp=event.timestamp,
                status=event.short_status or event.status,
                description=event.text or event.status,
                location=event.location,
            )
            for event in shipment.events
        ],
    )


def _from_unified(result: TrackingShipments, tracking_number: str) -> TrackingResult:
    if not result.shipments:
        return TrackingResult(tracking_number=tracking_number, source="unified", events=[])
    return _unified_shipment(result.shipments[0], tracking_number)


def _unified_shipment(shipment: TrackingShipment, fallback_number: str) -> TrackingResult:
    status = shipment.status
    status_code = status.status_code.root if status is not None else None
    return TrackingResult(
        tracking_number=shipment.id or fallback_number,
        source="unified",
        status_code=status_code,
        status=status.status if status else None,
        description=status.description if status else None,
        timestamp=status.timestamp if status else None,
        delivered=status_code == "delivered",
        returned=shipment.return_flag.root if shipment.return_flag else False,
        events=[
            TrackingEvent(
                timestamp=event.timestamp,
                status=event.status,
                description=event.description,
                location=_unified_location(event),
            )
            for event in (shipment.events or [])
        ],
    )


def _unified_location(event: object) -> str | None:
    location = getattr(event, "location", None)
    address = getattr(location, "address", None)
    return getattr(address, "address_locality", None)
