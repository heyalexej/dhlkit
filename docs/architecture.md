# Architecture

`dhlkit` separates transport, authentication, resource behavior, and wire models so
facts learned from one DHL API cannot leak into another.

```text
httpx sync/async clients
        │
        ▼
transport.py ── timeout, retry, error parsing, secret-safe metadata logging
        │
        ▼
per-resource auth strategy ── ROPC Bearer / legacy Basic / API-key header
        │
        ▼
resources/ ── hand-curated paths, methods, parameters, XML mapping
        │
        ├── generated/models/ ── Pydantic v2 models from official OpenAPI files
        │
        └── tracking_legacy.py ── pydantic-xml adapter (no OpenAPI exists)
```

## Boundaries

The transport owns connection handling, explicit timeouts, response parsing, and retry
policy. It asks the resource's authentication strategy for headers immediately before
each attempt, allowing a stale ROPC token to be invalidated and minted once after a
`401`.

Resources own DHL-specific behavior: URL, HTTP method, parameter spelling, response
model, and any verified normalization. The exact credential/header behavior is linked
from [the authentication matrix](AUTH.md). It is never inferred from OpenAPI security
declarations.

OpenAPI documents under `specs/` are model-only inputs. `_gen.py` strips all security
declarations before invoking `datamodel-code-generator`, then emits files carrying a
`DO NOT EDIT` banner. The source documents are excluded from published artifacts while
the generated models ship in the wheel.

Legacy Tracking is intentionally different. Its recursive `data` XML is parsed first
with `pydantic-xml`, then mapped into stable JSON-friendly models. Both the sibling
event-list shape in DHL's portal example and the nested event-list shape returned by
production are supported.

## Security

SDK logs include operation name, method, host, path, status, and elapsed time only.
Query strings are omitted because the legacy XML query contains GKP credentials.
Credential-like mapping keys are recursively masked by `dhlkit.logging.redact_secrets`.
File caches and the documented JSON config require mode `0600`.
