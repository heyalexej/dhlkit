from __future__ import annotations

from dhlkit.generated.models.tracking_unified import TrackingShipments
from dhlkit.pagination import paginate


def test_paginate_follows_next_url() -> None:
    offsets: list[str | None] = []

    def method(*, offset: str | None = None, limit: str | None = None):
        offsets.append(offset)
        if offset is None:
            return TrackingShipments.model_validate(
                {
                    "nextUrl": "https://api.example/track/shipments?offset=1&limit=1",
                    "shipments": [{"id": "one"}],
                }
            )
        return TrackingShipments.model_validate({"shipments": [{"id": "two"}]})

    items = list(paginate(method))

    assert [item.id for item in items] == ["one", "two"]
    assert offsets == [None, "1"]
