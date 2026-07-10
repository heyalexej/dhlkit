from __future__ import annotations

import json

import httpx
import pytest

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


@pytest.mark.anyio
async def test_basic_auth_sync_and_async_headers_match(config) -> None:
    auth = BasicKeySecretAuth(config)
    transport = httpx.MockTransport(lambda _request: httpx.Response(200))
    with httpx.Client(transport=transport) as client:
        sync_headers = auth.headers(client)
    async with httpx.AsyncClient(transport=transport) as aclient:
        async_headers = await auth.headers_async(aclient)

    assert sync_headers == async_headers
    assert async_headers["DHL-API-Key"] == "test-api-key"


@pytest.mark.anyio
async def test_apikey_auth_sync_and_async_headers_match(config) -> None:
    auth = ApiKeyHeaderAuth(config)
    transport = httpx.MockTransport(lambda _request: httpx.Response(200))
    with httpx.Client(transport=transport) as client:
        sync_headers = auth.headers(client)
    async with httpx.AsyncClient(transport=transport) as aclient:
        async_headers = await auth.headers_async(aclient)

    assert sync_headers == async_headers == {"dhl-api-key": "test-api-key"}


class _CountingCache:
    def __init__(self) -> None:
        self._inner = InMemoryTokenCache()
        self.gets = 0

    def get(self, key: str) -> CachedToken | None:
        self.gets += 1
        return self._inner.get(key)

    def set(self, key: str, token: CachedToken) -> None:
        self._inner.set(key, token)

    def clear(self, key: str) -> None:
        self._inner.clear(key)


def test_ropc_memoizes_token_and_skips_cache_reads(config) -> None:
    mints = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal mints
        mints += 1
        return httpx.Response(
            200,
            json={"access_token": f"token-{mints}", "token_type": "Bearer", "expires_in": 1800},
        )

    cache = _CountingCache()
    auth = RopcBearerAuth(config, cache, clock=lambda: 100.0)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        for _ in range(5):
            assert auth.headers(client)["Authorization"] == "Bearer token-1"

    assert mints == 1  # token minted once
    assert cache.gets <= 2  # only probed on the cold mint; the in-memory memo serves the rest


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
