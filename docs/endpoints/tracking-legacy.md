# Parcel DE Legacy Tracking v0

| Item | Value |
|---|---|
| Production URL | `https://api-eu.dhl.com/parcel/de/tracking/v0/shipments` |
| Method | `GET`, with XML in the `xml` query parameter |
| Authentication | [Legacy Tracking row in `AUTH.md`](../AUTH.md) |
| Verified app limit | 10,000,000 calls/day |
| Specification | No OpenAPI; official WADL/portal documentation |

`tracking.legacy()` accepts one number or a sequence of at most 15. Its result is a
`LegacyTrackingResult` containing typed shipments and an events list. Both production's
nested event list and the portal example's sibling shape are parsed.

```python
from dhlkit import DhlClient, DhlConfig

with DhlClient(DhlConfig.from_env()) as dhl:
    result = dhl.tracking.legacy(
        ["00340434780401935407", "00340434123456789012"],
        language="de",
    )
    for shipment in result.shipments:
        print(shipment.piece_code, len(shipment.events))
```

The encoded XML request template is:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<data
  appname="${DHL_GKP_USER}"
  password="${DHL_GKP_PASSWORD}"
  language-code="de"
  request="d-get-piece-detail"
  piece-code="number-1;number-2"
  zip-code="optional-postal-code"
  from-date="optional-YYYY-MM-DD"
  to-date="optional-YYYY-MM-DD" />
```

| XML field | SDK input |
|---|---|
| `piece-code` | `tracking_numbers` joined by `;` |
| `piece-customer-reference` | `customer_references` joined by `;` |
| `zip-code` | `postal_code` |
| `language-code` | `language` (`de`/`en`) |
| `from-date`, `to-date` | optional date window |

Source: [official DHL Parcel DE Shipment Tracking reference](https://developer.dhl.com/api-reference/dhl-parcel-de-shipment-tracking-post-parcel-germany), reviewed 2026-07-10. The production nesting difference was live-verified on that date and recorded in [gotchas](../gotchas.md#production-nests-legacy-event-lists).
