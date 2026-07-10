# dhlkit

`dhlkit` is an unofficial, typed Python SDK for the small set of DHL Parcel DE APIs
used by real shipping tools. It keeps each resource's empirically verified
authentication and HTTP behavior next to the code that sends the request, preventing
subtle gateway mistakes such as authenticating legacy tracking with GKP credentials or
calling postnumber verification with `GET`.

## Install

```shell
uv add dhlkit
```

The optional command-line interface is available with `uv add 'dhlkit[cli]'`.

## Quickstart

```python
from dhlkit import DhlClient, DhlConfig

config = DhlConfig.from_env()

with DhlClient(config) as dhl:
    locations = dhl.pickup.locations()
    verified = dhl.postnumber.verify(
        "871902603",
        firstname="Max",
        lastname="Mustermann",
    )
    shipment = dhl.tracking.legacy("00340434780401935407")

print(len(locations), verified.valid, shipment.shipments[0].status)
```

Set `DHL_API_KEY`, `DHL_API_SECRET`, `DHL_GKP_USER`, and `DHL_GKP_PASSWORD`, or
place them in a mode-`0600` XDG config file and use
`DhlConfig.from_file()`. See [the authentication source of truth](docs/AUTH.md) for
credential setup.

## Authentication model

DHL does not use one global authentication scheme. Pickup and postnumber use a cached
ROPC Bearer token, legacy tracking uses developer-app Basic authentication plus GKP
credentials in XML, and Unified Tracking uses one API-key header. OpenAPI security
declarations are not used because they do not consistently reflect gateway behavior.
The exact header and credential matrix lives only in [docs/AUTH.md](docs/AUTH.md).

## Supported APIs

| API / operation | SDK method | Verified app limit |
|---|---|---:|
| ROPC token | automatic | token TTL about 30 minutes |
| Pickup v3 | `pickup.locations/create/get/cancel` | 500,000/day |
| Postnumber v1 | `postnumber.verify` | 50,000/day |
| Legacy Tracking v0 | `tracking.legacy` | 10,000,000/day |
| Unified Tracking | `tracking.unified` | 250/day default |

> DHL's most misleading behaviors are recorded in [the gotchas guide](docs/gotchas.md)
> and protected by named offline regression tests.

Both `DhlClient` and `AsyncDhlClient` accept an `httpx` client for integration with an
existing connection pool. Every SDK-created client has an explicit timeout. Transient
idempotent requests are retried with bounded exponential backoff, and an ROPC-protected
request refreshes its token once after a `401`.

## Regenerating models

Official OpenAPI YAML files under `specs/` are model inputs only. Authentication is
hand-curated. To regenerate and verify committed output:

```shell
uv sync
uv run python -m dhlkit._gen
uv run python -m dhlkit._gen --check
```

Generated files under `src/dhlkit/generated/models/` must not be edited by hand. Commit
a changed source spec and its regenerated models together.

## Contributing

Run `just check` before submitting a change. Live smoke tests are opt-in with
`just live` and require all four credentials; the normal suite is fully offline.

Commits follow `type(scope): imperative summary`, for example
`fix(tracking): preserve legacy event lists`. User-visible changes also belong under
`Unreleased` in [CHANGELOG.md](CHANGELOG.md).

`dhlkit` is released under the [MIT License](LICENSE). DHL and its product names are
trademarks of their respective owner; this project is not affiliated with DHL.
