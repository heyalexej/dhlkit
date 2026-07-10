# Shipment Tracking Unified

| Item | Value |
|---|---|
| Production URL | `https://api-eu.dhl.com/track/shipments` |
| Method | `GET` |
| Authentication | [Unified Tracking row in `AUTH.md`](../AUTH.md) |
| Default limit | 250 calls/day |
| OpenAPI | `specs/track-unified.yaml` |

`tracking.unified()` sends `trackingNumber` and defaults `service` to `parcel-de`.
Optional country, recipient postal code, language, offset, and limit parameters map
directly to the generated `TrackingShipments` response.

```python
from dhlkit import DhlClient, DhlConfig

with DhlClient(DhlConfig.from_env()) as dhl:
    result = dhl.tracking.unified(
        "CB248249614DE",
        service="parcel-de",
        language="de",
    )
    for shipment in result.shipments or []:
        print(shipment.id, shipment.status.status_code.root)
```

Source: [official Shipment Tracking Unified reference](https://developer.dhl.com/api-reference/shipment-tracking), OpenAPI version 1.5.8 fetched 2026-07-10 from the portal's published YAML.
