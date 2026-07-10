from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from dhlkit.generated.models.pickup import (
    CancelResult,
    OrderResponse,
    PickupLocationId,
    PickupOrder,
    PickupOrderStatus,
)
from dhlkit.resource import AsyncResource, Resource


class PickupResource(Resource):
    """Parcel DE Pickup v3 using ROPC Bearer auth (``docs/AUTH.md``)."""

    def locations(self, *, postal_code: str | None = None) -> list[PickupLocationId]:
        """Return agreed pickup locations using Bearer auth; see ``docs/AUTH.md``."""
        return self._request(
            "pickup.locations",
            "GET",
            "/locations",
            params={"postalCode": postal_code},
            response_model=list[PickupLocationId],
        )

    def create(
        self,
        order: PickupOrder | Mapping[str, Any],
        *,
        as_id: str | None = None,
        validate: bool = False,
    ) -> OrderResponse:
        """Create or validate a pickup order using Bearer auth; see ``docs/AUTH.md``."""
        normalized = _pickup_order(order, as_id=as_id)
        return self._request(
            "pickup.create",
            "POST",
            "/orders",
            params={"validate": str(validate).lower()},
            body=normalized,
            response_model=OrderResponse,
        )

    def get(
        self,
        *,
        order_id: str | None = None,
        pickup_date: str | None = None,
        pickup_name1: str | None = None,
        pickup_address_street: str | None = None,
        pickup_address_house: str | None = None,
        pickup_postal_code: str | None = None,
        pickup_city: str | None = None,
    ) -> list[PickupOrderStatus]:
        """Get pickup status using ROPC Bearer auth; see ``docs/AUTH.md``."""
        if order_id is None and pickup_date is None:
            raise ValueError("order_id or pickup_date is required")
        return self._request(
            "pickup.get",
            "GET",
            "/orders",
            params={
                "orderID": order_id,
                "pickupDate": pickup_date,
                "pickupName1": pickup_name1,
                "pickupAddressStreet": pickup_address_street,
                "pickupAddressHouse": pickup_address_house,
                "pickupPostalCode": pickup_postal_code,
                "pickupCity": pickup_city,
            },
            response_model=list[PickupOrderStatus],
        )

    def cancel(self, order_ids: str | Sequence[str]) -> CancelResult:
        """Cancel one or more pickup orders using Bearer auth; see ``docs/AUTH.md``."""
        values = [order_ids] if isinstance(order_ids, str) else list(order_ids)
        if not values:
            raise ValueError("at least one order ID is required")
        return self._request(
            "pickup.cancel",
            "DELETE",
            "/orders",
            params={"orderID": values},
            response_model=CancelResult,
        )


class AsyncPickupResource(AsyncResource):
    """Asynchronous Parcel DE Pickup v3 resource."""

    async def locations(self, *, postal_code: str | None = None) -> list[PickupLocationId]:
        return await self._request(
            "pickup.locations",
            "GET",
            "/locations",
            params={"postalCode": postal_code},
            response_model=list[PickupLocationId],
        )

    async def create(
        self,
        order: PickupOrder | Mapping[str, Any],
        *,
        as_id: str | None = None,
        validate: bool = False,
    ) -> OrderResponse:
        normalized = _pickup_order(order, as_id=as_id)
        return await self._request(
            "pickup.create",
            "POST",
            "/orders",
            params={"validate": str(validate).lower()},
            body=normalized,
            response_model=OrderResponse,
        )

    async def get(
        self,
        *,
        order_id: str | None = None,
        pickup_date: str | None = None,
        pickup_name1: str | None = None,
        pickup_address_street: str | None = None,
        pickup_address_house: str | None = None,
        pickup_postal_code: str | None = None,
        pickup_city: str | None = None,
    ) -> list[PickupOrderStatus]:
        if order_id is None and pickup_date is None:
            raise ValueError("order_id or pickup_date is required")
        return await self._request(
            "pickup.get",
            "GET",
            "/orders",
            params={
                "orderID": order_id,
                "pickupDate": pickup_date,
                "pickupName1": pickup_name1,
                "pickupAddressStreet": pickup_address_street,
                "pickupAddressHouse": pickup_address_house,
                "pickupPostalCode": pickup_postal_code,
                "pickupCity": pickup_city,
            },
            response_model=list[PickupOrderStatus],
        )

    async def cancel(self, order_ids: str | Sequence[str]) -> CancelResult:
        values = [order_ids] if isinstance(order_ids, str) else list(order_ids)
        if not values:
            raise ValueError("at least one order ID is required")
        return await self._request(
            "pickup.cancel",
            "DELETE",
            "/orders",
            params={"orderID": values},
            response_model=CancelResult,
        )


def _pickup_order(
    order: PickupOrder | Mapping[str, Any],
    *,
    as_id: str | None,
) -> PickupOrder:
    payload = (
        order.model_dump(by_alias=True, exclude_none=True)
        if isinstance(order, PickupOrder)
        else dict(order)
    )
    location = dict(payload.get("pickupLocation") or payload.get("pickup_location") or {})
    if as_id is not None:
        location["asId"] = as_id
    if location.get("type") == "Id" or "asId" in location or "id" in location:
        # ``asId`` is the actual wire field; ``id`` looks plausible but is rejected
        # by DHL (verified 2026-07-09, see docs/gotchas.md).
        if "asId" not in location and "id" in location:
            location["asId"] = location.pop("id")
        location["type"] = "Id"
        location.pop("id", None)
        payload.pop("pickup_location", None)
        payload["pickupLocation"] = location
    return PickupOrder.model_validate(payload)
