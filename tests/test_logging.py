from __future__ import annotations

from dhlkit.logging import redact_secrets


def test_redaction_masks_nested_secret_values() -> None:
    event = {
        "authorization": "Bearer sensitive-token",
        "nested": {"api_key": "sensitive-key", "status": 200},
        "items": [{"password": "sensitive-password"}],
    }

    redacted = redact_secrets(None, "info", event)
    rendered = repr(redacted)

    assert "sensitive-token" not in rendered
    assert "sensitive-key" not in rendered
    assert "sensitive-password" not in rendered
    assert redacted["nested"]["status"] == 200
