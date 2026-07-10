# Verified DHL gotchas

These entries are behavioral facts established against the DHL gateway. Authentication
header details live in [the source-of-truth matrix](AUTH.md); this file records symptoms,
causes, fixes, and proof. Each behavior has a named offline regression test.

## Postnumber must use POST

- **Symptom:** `GET /customers/{postnumber}` returns a misleading `401 Unauthorized`.
- **Cause:** the verification operation accepts the customer name in a JSON body and is
  implemented as `POST`.
- **Fix:** `postnumber.verify()` always constructs `POST`.
- **Proof:** same Bearer token and identity, GET→401 / POST→200 on 2026-07-09.
- **Regression:** [`test_postnumber_uses_post_not_get`](../tests/test_gotchas.py).

## Legacy Basic credentials are the app pair

- **Symptom:** Basic authentication with the GKP login returns `401 Invalid ApiKey`.
- **Cause:** the gateway Basic pair is the developer app key and secret.
- **Fix:** `BasicKeySecretAuth` encodes only the app credential pair.
- **Proof:** GKP pair→401 / app pair→200 on 2026-07-09.
- **Regression:** [`test_legacy_tracking_basic_is_key_secret`](../tests/test_gotchas.py).

## Legacy GKP credentials belong in XML

- **Symptom:** gateway authentication can succeed while the tracking XML reports login
  failure.
- **Cause:** the v0 service has a second authentication layer inside `appname` and
  `password` XML attributes.
- **Fix:** the XML builder inserts the GKP pair; headers never do.
- **Proof:** successful business query on 2026-07-09.
- **Regression:** [`test_legacy_tracking_gkp_creds_in_xml`](../tests/test_gotchas.py).

## Pickup location uses `type: Id` and `asId`

- **Symptom:** a plausible `{id: "AS…"}` pickup location fails validation.
- **Cause:** the v3 discriminator and wire field are `type="Id"` and `asId`.
- **Fix:** `pickup.create()` normalizes the ID form before Pydantic validation.
- **Proof:** accepted live request shape on 2026-07-09.
- **Regression:** [`test_pickup_location_type_id_and_asid`](../tests/test_gotchas.py).

## Unified Tracking's header is lowercase

- **Symptom:** integrations can drift from the portal's exact subscription-key contract.
- **Cause:** this product defines `dhl-api-key`; it is independent of Parcel DE Bearer
  resources.
- **Fix:** `ApiKeyHeaderAuth` emits that exact spelling and no other auth header.
- **Proof:** Unified request returned `200` on 2026-07-09 and again on 2026-07-10.
- **Regression:** [`test_unified_apikey_header_lowercase`](../tests/test_gotchas.py).

## Bearer and API-key auth cannot be combined

- **Symptom:** the gateway rejects a request with “use EITHER Bearer or Apikey”.
- **Cause:** headers from separate DHL product schemes were combined globally.
- **Fix:** authentication is attached to each resource.
- **Proof:** combined headers rejected / Bearer-only Pickup accepted on 2026-07-09.
- **Regression:** [`test_no_bearer_and_apikey_together`](../tests/test_gotchas.py).

## ROPC tokens should be reused

- **Symptom:** minting a token for every resource call adds latency and needless auth
  traffic.
- **Cause:** the token's approximately 30-minute lifetime was ignored.
- **Fix:** cache until expiry with a 30-second skew; invalidate once after `401`.
- **Proof:** repeated calls accepted the same token until its TTL on 2026-07-09.
- **Regression:** [`test_ropc_token_reused_until_expiry`](../tests/test_gotchas.py).

## One XML event is still a list

- **Symptom:** code handles multiple `<data name="pieceevent">` nodes but crashes when
  only one is present.
- **Cause:** XML-to-object tools often collapse a single repeated element.
- **Fix:** the pydantic-xml node declares `children` as a list unconditionally.
- **Proof:** recorded one-event and multi-event responses, 2026-07-09.
- **Regression:** [`test_tracking_legacy_single_event_is_list`](../tests/test_gotchas.py).

## Production nests legacy event lists

- **Symptom:** shipment summaries parse, but `events` is empty even though tracking has a
  long history.
- **Cause:** the portal example shows `pieceeventlist` beside `pieceshipment`; production
  returns `piece-event-list` nested inside `piece-shipment`.
- **Fix:** accept both sibling and nested spellings/shapes.
- **Proof:** schema-only inspection of production XML and 120 read-only shipment probes
  on 2026-07-10; the selected sanitized return fixture contains 13 events.
- **Regression:**
  [`test_legacy_tracking_live_nested_events_are_preserved`](../tests/test_gotchas.py).

The committed long-history fixtures replace every identifier, location, and timestamp;
remove person/address/reference fields; and scrub tracking IDs embedded inside status
URLs. The recorder runs a protected-value leak check before fixture promotion.
