from __future__ import annotations

from typing import Literal

from dhlkit.generated.models.tracking_unified import TrackingShipments
from dhlkit.resource import AsyncResource, Resource


class UnifiedTrackingResource(Resource):
    """Unified Tracking using only lowercase API-key auth (``docs/AUTH.md``)."""

    def track(
        self,
        tracking_number: str,
        *,
        service: str = "parcel-de",
        requester_country_code: str | None = None,
        origin_country_code: str | None = None,
        recipient_postal_code: str | None = None,
        language: Literal["en", "de"] | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> TrackingShipments:
        """Retrieve Unified Tracking JSON using API-key-only auth; see ``docs/AUTH.md``."""
        return self._request(
            "tracking.unified",
            "GET",
            "/shipments",
            params={
                "trackingNumber": tracking_number,
                "service": service,
                "requesterCountryCode": requester_country_code,
                "originCountryCode": origin_country_code,
                "recipientPostalCode": recipient_postal_code,
                "language": language,
                "offset": offset,
                "limit": limit,
            },
            response_model=TrackingShipments,
        )


class AsyncUnifiedTrackingResource(AsyncResource):
    """Asynchronous Unified Tracking resource."""

    async def track(
        self,
        tracking_number: str,
        *,
        service: str = "parcel-de",
        requester_country_code: str | None = None,
        origin_country_code: str | None = None,
        recipient_postal_code: str | None = None,
        language: Literal["en", "de"] | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> TrackingShipments:
        return await self._request(
            "tracking.unified",
            "GET",
            "/shipments",
            params={
                "trackingNumber": tracking_number,
                "service": service,
                "requesterCountryCode": requester_country_code,
                "originCountryCode": origin_country_code,
                "recipientPostalCode": recipient_postal_code,
                "language": language,
                "offset": offset,
                "limit": limit,
            },
            response_model=TrackingShipments,
        )
