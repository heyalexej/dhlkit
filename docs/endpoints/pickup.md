# Parcel DE Pickup v3

| Item | Value |
|---|---|
| Production base | `https://api-eu.dhl.com/parcel/de/transportation/pickup/v3` |
| Methods | `GET /locations`, `POST/GET/DELETE /orders` |
| Authentication | [Pickup row in `AUTH.md`](../AUTH.md) |
| Verified app limit | 500,000 calls/day |
| OpenAPI | `specs/pickup-v3.yaml` |

The SDK returns generated `PickupLocationId`, `OrderResponse`, `PickupOrderStatus`, and
`CancelResult` models. `create()` accepts a generated `PickupOrder` or mapping and
normalizes agreed-location IDs as described in [the gotcha](../gotchas.md#pickup-location-uses-type-id-and-asid).

```python
from dhlkit import DhlClient, DhlConfig

order = {
    "customerDetails": {"billingNumber": "123456789012AB"},
    "pickupLocation": {"asId": "AS1234567890", "type": "Id"},
    "pickupDetails": {"pickupDate": {"type": "ASAP"}},
    "shipmentDetails": {"shipments": [{"transportationType": "PAKET"}]},
}

with DhlClient(DhlConfig.from_env()) as dhl:
    locations = dhl.pickup.locations(postal_code="53113")
    confirmation = dhl.pickup.create(order, validate=True)
```

Source: [official DHL Parcel DE Pickup reference](https://developer.dhl.com/api-reference/dhl-parcel-de-pickup-post-parcel-germany), OpenAPI version 3.0.0 fetched 2026-07-10 from the portal's published YAML.
