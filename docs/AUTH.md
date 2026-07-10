# DHL Parcel DE — Auth Matrix (empirically verified)

Source of truth for auth. **Do NOT trust the OpenAPI `securitySchemes`** — several
are wrong (e.g. Postnumber's spec declares `BasicAuth`+`ApiKey` but the endpoint
only works with the ROPC Bearer token). Verified live 2026-07-08/09. Generator
emits MODELS from the specs; the auth layer is hand-curated from this table.

Credentials (env / config):
- `api_key` (DHL_API_KEY), `api_secret` (DHL_API_SECRET) — the developer app
- `gkp_user` (DHL_GKP_USER), `gkp_password` (DHL_GKP_PASSWORD) — GKP login

| Endpoint | Base URL | Method | VERIFIED auth | Gotchas |
|---|---|---|---|---|
| Token (ROPC) | `api-eu.dhl.com/parcel/de/account/auth/ropc/v1/token` | POST (form) | `grant_type=password`, `client_id=api_key`, `client_secret=api_secret`, `username=gkp_user`, `password=gkp_password` | returns opaque Bearer, `expires_in` ≈ 1800s (30 min) |
| Pickup v3 | `…/parcel/de/transportation/pickup/v3` | GET/POST/DELETE | **Bearer** (ROPC) | Bearer **only** — do NOT also send `dhl-api-key` (gateway: "use EITHER Bearer or Apikey"). `pickupLocation` = `{type:"Id", asId:"AS…"}`. |
| Postnumber v1 | `…/parcel/de/account/postnumber/v1/customers/{pn}` | **POST** | **Bearer** (ROPC) | POST, **not GET** (GET → misleading 401 "Unauthorized for given resource"). Body `{firstname,lastname}`. Spec's declared auth is wrong. |
| Legacy Tracking v0 | `api-eu.dhl.com/parcel/de/tracking/v0/shipments?xml=…` | GET | **HTTP Basic = base64(`api_key`:`api_secret`)** + `DHL-API-Key` header; **GKP user/pass go in the XML** `appname`/`password` | Two auth layers. Basic is key:secret, **NOT** the GKP creds (that gave 401 "Invalid ApiKey"). GKP user needs the "Verfolgen Paket & Waren" right. `request="d-get-piece-detail"`, ≤15 numbers/refs per call, 3-month window. No OpenAPI spec (WADL/XML legacy). |
| Unified Tracking | `api-eu.dhl.com/track/shipments?trackingNumber=…&service=parcel-de` | GET | **`dhl-api-key` header only** (lowercase) | Separate product subscription (own entitlement). Default 250/day. JSON. |

## Auth strategies the SDK needs (3, not 1)
1. **RopcBearerAuth** — token cache (30-min TTL, refresh-on-401), used by Pickup and Postnumber.
2. **BasicKeySecretAuth** — `Authorization: Basic base64(api_key:api_secret)` + `DHL-API-Key` header — legacy Tracking only. GKP creds handled separately (XML body builder).
3. **ApiKeyHeaderAuth** — `dhl-api-key` header (lowercase) — Unified Tracking.

## Local specs (for MODEL codegen; NOT auth)
- `auth-ropc.yaml` (v2.0.5), `pickup-v3.yaml` (v3.0.0),
  `postnumber-v1.yaml` (v1.0.1), and `track-unified.yaml` (v1.5.8) are saved under
  `specs/`.
- Legacy Tracking v0 — **no spec exists**; the XML adapter is hand-written from this file.


## Credential setup

The four values are two separate credential pairs: a developer-application pair and a
business-portal pair. Obtain and rotate them through the corresponding official DHL
portals.

| Environment variable | Meaning |
|---|---|
| `DHL_API_KEY` | developer-application client ID |
| `DHL_API_SECRET` | developer-application client secret |
| `DHL_GKP_USER` | business-portal user |
| `DHL_GKP_PASSWORD` | business-portal password |

`DhlConfig.from_env()` reads the variables above. `DhlConfig.from_file()` reads a JSON
object from `~/.config/dhlkit/config.json` by default and requires mode `0600`. Bearer
tokens are cached at `~/.cache/dhlkit/tokens.json`, also mode `0600`.

Never print or commit credentials or token-cache contents. `.env` and `config.json` are
git-ignored, and CI does not receive secrets. The live suite skips when any required
credential is absent.
