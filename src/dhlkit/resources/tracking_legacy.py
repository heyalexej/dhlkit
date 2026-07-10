from __future__ import annotations

from collections.abc import Sequence
from typing import Literal
from xml.sax.saxutils import quoteattr

from pydantic import ConfigDict
from pydantic_xml import BaseXmlModel, attr, element
from pydantic_xml.element import SearchMode

from dhlkit.auth.base import AuthStrategy
from dhlkit.config import DhlConfig
from dhlkit.errors import DhlAPIError
from dhlkit.models import DhlModel
from dhlkit.resource import AsyncResource, Resource


class LegacyXmlNode(BaseXmlModel, tag="data", search_mode=SearchMode.UNORDERED):
    """Recursive model for the legacy API's attribute-heavy ``data`` elements."""

    model_config = ConfigDict(extra="ignore")

    name: str | None = attr(default=None)
    code: str | None = attr(default=None)
    request_id: str | None = attr(name="request-id", default=None)
    error_status: str | None = attr(name="error-status", default=None)
    piece_id: str | None = attr(name="piece-id", default=None)
    piece_identifier: str | None = attr(name="piece-identifier", default=None)
    piece_code: str | None = attr(name="piece-code", default=None)
    searched_piece_code: str | None = attr(name="searched-piece-code", default=None)
    piece_customer_reference: str | None = attr(name="piece-customer-reference", default=None)
    status_timestamp: str | None = attr(name="status-timestamp", default=None)
    status: str | None = attr(default=None)
    short_status: str | None = attr(name="short-status", default=None)
    product_name: str | None = attr(name="product-name", default=None)
    delivery_event_flag: str | None = attr(name="delivery-event-flag", default=None)
    return_flag: str | None = attr(name="ruecksendung", default=None)
    event_timestamp: str | None = attr(name="event-timestamp", default=None)
    event_status: str | None = attr(name="event-status", default=None)
    event_text: str | None = attr(name="event-text", default=None)
    event_short_status: str | None = attr(name="event-short-status", default=None)
    event_location: str | None = attr(name="event-location", default=None)
    event_country: str | None = attr(name="event-country", default=None)
    ice: str | None = attr(default=None)
    ric: str | None = attr(default=None)
    standard_event_code: str | None = attr(name="standard-event-code", default=None)
    children: list[LegacyXmlNode] = element(tag="data", default_factory=list)


class LegacyTrackingEvent(DhlModel):
    timestamp: str | None = None
    status: str | None = None
    text: str | None = None
    short_status: str | None = None
    location: str | None = None
    country: str | None = None
    ice: str | None = None
    ric: str | None = None
    standard_event_code: str | None = None


class LegacyShipment(DhlModel):
    piece_id: str | None = None
    piece_identifier: str | None = None
    piece_code: str | None = None
    searched_piece_code: str | None = None
    customer_reference: str | None = None
    error_status: str | None = None
    status_timestamp: str | None = None
    status: str | None = None
    short_status: str | None = None
    product_name: str | None = None
    delivered: bool = False
    returned: bool = False
    events: list[LegacyTrackingEvent]


class LegacyTrackingResult(DhlModel):
    request_id: str | None = None
    code: str | None = None
    shipments: list[LegacyShipment]


class LegacyTrackingResource(Resource):
    """Legacy Tracking v0 with Basic app auth and GKP credentials in XML."""

    def __init__(
        self,
        client: object,
        auth: AuthStrategy,
        base_url: str,
        config: DhlConfig,
    ) -> None:
        super().__init__(client, auth, base_url)
        self._config = config

    def track(
        self,
        tracking_numbers: str | Sequence[str] | None = None,
        *,
        customer_references: str | Sequence[str] | None = None,
        postal_code: str | None = None,
        language: Literal["de", "en"] = "de",
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> LegacyTrackingResult:
        """Track through v0 using app Basic auth; GKP auth stays in XML (``docs/AUTH.md``)."""
        xml = _request_xml(
            self._config,
            tracking_numbers,
            customer_references=customer_references,
            postal_code=postal_code,
            language=language,
            from_date=from_date,
            to_date=to_date,
        )
        return self._request(
            "tracking.legacy",
            "GET",
            "/shipments",
            params={"xml": xml},
            headers={"Accept": "application/xml, text/xml"},
            response_parser=_parse_response,
        )


class AsyncLegacyTrackingResource(AsyncResource):
    """Asynchronous Legacy Tracking v0 resource."""

    def __init__(
        self,
        client: object,
        auth: AuthStrategy,
        base_url: str,
        config: DhlConfig,
    ) -> None:
        super().__init__(client, auth, base_url)
        self._config = config

    async def track(
        self,
        tracking_numbers: str | Sequence[str] | None = None,
        *,
        customer_references: str | Sequence[str] | None = None,
        postal_code: str | None = None,
        language: Literal["de", "en"] = "de",
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> LegacyTrackingResult:
        xml = _request_xml(
            self._config,
            tracking_numbers,
            customer_references=customer_references,
            postal_code=postal_code,
            language=language,
            from_date=from_date,
            to_date=to_date,
        )
        return await self._request(
            "tracking.legacy",
            "GET",
            "/shipments",
            params={"xml": xml},
            headers={"Accept": "application/xml, text/xml"},
            response_parser=_parse_response,
        )


def _request_xml(
    config: DhlConfig,
    tracking_numbers: str | Sequence[str] | None,
    *,
    customer_references: str | Sequence[str] | None,
    postal_code: str | None,
    language: str,
    from_date: str | None,
    to_date: str | None,
) -> str:
    numbers = _values(tracking_numbers)
    references = _values(customer_references) if customer_references is not None else []
    if references and numbers:
        raise ValueError("pass tracking numbers or customer references, not both")
    selected = references or numbers
    if not 1 <= len(selected) <= 15:
        raise ValueError("legacy tracking accepts between 1 and 15 identifiers")

    attributes = {
        "appname": config.require_gkp_user(),
        "password": config.require_gkp_password(),
        "language-code": language,
        "request": "d-get-piece-detail",
        "piece-customer-reference" if references else "piece-code": ";".join(selected),
        "zip-code": postal_code,
        "from-date": from_date,
        "to-date": to_date,
    }
    serialized = " ".join(
        f"{name}={quoteattr(value)}" for name, value in attributes.items() if value is not None
    )
    return f'<?xml version="1.0" encoding="UTF-8"?><data {serialized}/>'


def _values(value: str | Sequence[str] | None) -> list[str]:
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


def _parse_response(content: bytes) -> LegacyTrackingResult:
    root = LegacyXmlNode.from_xml(content)
    # The v0 service reports request-level failures (e.g. a rejected GKP login)
    # as HTTP 200 with a nonzero root ``code``; ``code="0"`` is success. Surface
    # these through DhlError instead of returning an empty, error-masking result.
    if root.code is not None and root.code != "0":
        raise DhlAPIError(
            f"legacy tracking request failed with code {root.code}",
            status_code=200,
            title=root.name,
            detail=root.error_status,
        )
    event_lists = {
        node.piece_id or node.piece_identifier: node.children
        for node in root.children
        if node.name in {"pieceeventlist", "piece-event-list"}
    }
    shipments: list[LegacyShipment] = []
    for node in root.children:
        if node.name not in {"pieceshipment", "piece-shipment", "piece-status-public"}:
            continue
        # The portal example shows event lists as siblings, while the live v0
        # response nests ``piece-event-list`` below ``piece-shipment``. Support
        # both shapes (live nesting verified 2026-07-10).
        nested_events = [
            event
            for event_list in node.children
            if event_list.name in {"pieceeventlist", "piece-event-list"}
            for event in event_list.children
        ]
        sibling_events = event_lists.get(node.piece_id or node.piece_identifier, [])
        shipments.append(_shipment(node, nested_events or sibling_events))
    return LegacyTrackingResult(
        request_id=root.request_id,
        code=root.code,
        shipments=shipments,
    )


def _shipment(node: LegacyXmlNode, events: list[LegacyXmlNode]) -> LegacyShipment:
    return LegacyShipment(
        piece_id=node.piece_id,
        piece_identifier=node.piece_identifier,
        piece_code=node.piece_code,
        searched_piece_code=node.searched_piece_code,
        customer_reference=node.piece_customer_reference,
        error_status=node.error_status,
        status_timestamp=node.status_timestamp,
        status=node.status,
        short_status=node.short_status,
        product_name=node.product_name,
        delivered=node.delivery_event_flag == "1",
        returned=(node.return_flag or "").lower() in {"1", "true"},
        events=[
            LegacyTrackingEvent(
                timestamp=event.event_timestamp,
                status=event.event_status,
                text=event.event_text,
                short_status=event.event_short_status,
                location=event.event_location,
                country=event.event_country,
                ice=event.ice,
                ric=event.ric,
                standard_event_code=event.standard_event_code,
            )
            for event in events
            if event.name in {"pieceevent", "piece-event"}
        ],
    )
