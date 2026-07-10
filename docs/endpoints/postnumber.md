# Parcel DE Postnumber v1

| Item | Value |
|---|---|
| Production base | `https://api-eu.dhl.com/parcel/de/account/postnumber/v1` |
| Method | `POST /customers/{postnumber}` |
| Authentication | [Postnumber row in `AUTH.md`](../AUTH.md) |
| Verified app limit | 50,000 calls/day |
| OpenAPI | `specs/postnumber-v1.yaml` |

The request body is `{firstname, lastname}`. A `200` or `412` response is parsed as a
generated `PostnumberResponse`; both therefore return a typed `valid` boolean. The SDK
never constructs the misleading GET form described in [the gotcha](../gotchas.md#postnumber-must-use-post).

```python
from dhlkit import DhlClient, DhlConfig

with DhlClient(DhlConfig.from_env()) as dhl:
    result = dhl.postnumber.verify(
        "871902603",
        firstname="Max",
        lastname="Mustermann",
    )
    print(result.valid)
```

Source: [official DHL Parcel DE Postnumber reference](https://developer.dhl.com/api-reference/dhl-paket-de-postnummern-post-paket-deutschland), OpenAPI version 1.0.1 fetched 2026-07-10 from the portal's published YAML.
