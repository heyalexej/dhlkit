from __future__ import annotations

import json

import httpx

from dhlkit.auth import (
    ApiKeyHeaderAuth,
    BasicKeySecretAuth,
    FileTokenCache,
    InMemoryTokenCache,
    RopcBearerAuth,
)
from dhlkit.auth.cache import CachedToken


def test_basic_auth_uses_developer_credentials(config) -> None:
    auth = BasicKeySecretAuth(config)
    transport = httpx.MockTransport(lambda _request: httpx.Response(200))
    with httpx.Client(transport=transport) as client:
        headers = auth.headers(client)

    assert headers["Authorization"] == "Basic dGVzdC1hcGkta2V5OnRlc3QtYXBpLXNlY3JldA=="
    assert headers["DHL-API-Key"] == "test-api-key"


def test_apikey_auth_has_only_lowercase_header(config) -> None:
    auth = ApiKeyHeaderAuth(config)
    transport = httpx.MockTransport(lambda _request: httpx.Response(200))
    with httpx.Client(transport=transport) as client:
        assert auth.headers(client) == {"dhl-api-key": "test-api-key"}


def test_ropc_cache_and_expiry(config) -> None:
    now = [100.0]
    token_requests = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal token_requests
        token_requests += 1
        payload = {
            "access_token": f"token-{token_requests}",
            "token_type": "Bearer",
            "expires_in": 1800,
        }
        return httpx.Response(200, json=payload)

    auth = RopcBearerAuth(config, InMemoryTokenCache(), clock=lambda: now[0])
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert auth.headers(client)["Authorization"] == "Bearer token-1"
        now[0] = 1800.0
        assert auth.headers(client)["Authorization"] == "Bearer token-1"
        now[0] = 1871.0
        assert auth.headers(client)["Authorization"] == "Bearer token-2"

    assert token_requests == 2


def test_file_token_cache_is_mode_0600(tmp_path) -> None:
    path = tmp_path / "tokens.json"
    cache = FileTokenCache(path)

    cache.set("app", CachedToken(access_token="sensitive", expires_at=123.0))

    assert path.stat().st_mode & 0o777 == 0o600
    assert cache.get("app") == CachedToken(access_token="sensitive", expires_at=123.0)
    assert json.loads(path.read_text())["app"]["access_token"] == "sensitive"


def test_cached_token_repr_is_redacted() -> None:
    token = CachedToken(access_token="never-print-this", expires_at=123.0)

    assert "never-print-this" not in repr(token)
    assert "redacted" in repr(token)


def test_file_token_cache_repairs_permissive_mode(tmp_path) -> None:
    path = tmp_path / "tokens.json"
    path.write_text('{"app":{"access_token":"token","expires_at":123}}')
    path.chmod(0o644)

    token = FileTokenCache(path).get("app")

    assert token is not None
    assert path.stat().st_mode & 0o777 == 0o600
