from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .pickup import AsyncPickupResource, PickupResource
from .postnumber import AsyncPostnumberResource, PostnumberResource
from .tracking_legacy import (
    AsyncLegacyTrackingResource,
    LegacyShipment,
    LegacyTrackingEvent,
    LegacyTrackingResource,
    LegacyTrackingResult,
)
from .tracking_unified import AsyncUnifiedTrackingResource, UnifiedTrackingResource


class TrackingResource:
    def __init__(
        self,
        legacy: LegacyTrackingResource,
        unified: UnifiedTrackingResource,
    ) -> None:
        self._legacy = legacy
        self._unified = unified

    def legacy(
        self,
        tracking_number: str | Sequence[str] | None = None,
        **kwargs: Any,
    ) -> LegacyTrackingResult:
        return self._legacy.track(tracking_number, **kwargs)

    def unified(self, tracking_number: str, **kwargs: Any) -> Any:
        return self._unified.track(tracking_number, **kwargs)


class AsyncTrackingResource:
    def __init__(
        self,
        legacy: AsyncLegacyTrackingResource,
        unified: AsyncUnifiedTrackingResource,
    ) -> None:
        self._legacy = legacy
        self._unified = unified

    async def legacy(
        self,
        tracking_number: str | Sequence[str] | None = None,
        **kwargs: Any,
    ) -> LegacyTrackingResult:
        return await self._legacy.track(tracking_number, **kwargs)

    async def unified(self, tracking_number: str, **kwargs: Any) -> Any:
        return await self._unified.track(tracking_number, **kwargs)


__all__ = [
    "AsyncPickupResource",
    "AsyncPostnumberResource",
    "AsyncTrackingResource",
    "LegacyShipment",
    "LegacyTrackingEvent",
    "LegacyTrackingResult",
    "PickupResource",
    "PostnumberResource",
    "TrackingResource",
]
