from __future__ import annotations

import asyncio
import hashlib
import threading
import time
from collections.abc import Callable

import httpx
import orjson

from dhlkit.auth.cache import CachedToken, TokenCache
from dhlkit.config import DhlConfig
from dhlkit.errors import DhlAuthError

_EXPIRY_SKEW_SECONDS = 30.0


class RopcBearerAuth:
    """Cached OAuth password-grant Bearer authentication for Parcel DE resources."""

    refreshes_on_401 = True

    def __init__(
        self,
        config: DhlConfig,
        cache: TokenCache,
        *,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._config = config
        self._cache = cache
        self._clock = clock
        self._sync_lock = threading.Lock()
        self._async_lock = asyncio.Lock()
        self._memo: CachedToken | None = None
        self._key: str | None = None

    def headers(self, client: httpx.Client) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._access_token(client)}"}

    async def headers_async(self, client: httpx.AsyncClient) -> dict[str, str]:
        return {"Authorization": f"Bearer {await self._access_token_async(client)}"}

    def invalidate(self) -> None:
        self._memo = None
        self._cache.clear(self._cache_key())

    def _access_token(self, client: httpx.Client) -> str:
        token = self._valid_cached_token()
        if token is not None:
            return token.access_token
        with self._sync_lock:
            token = self._valid_cached_token()
            return token.access_token if token is not None else self._mint(client).access_token

    async def _access_token_async(self, client: httpx.AsyncClient) -> str:
        token = self._valid_cached_token()
        if token is not None:
            return token.access_token
        async with self._async_lock:
            token = self._valid_cached_token()
            if token is not None:
                return token.access_token
            return (await self._mint_async(client)).access_token

    def _valid_cached_token(self) -> CachedToken | None:
        memo = self._memo
        if memo is not None and not self._is_expired(memo):
            return memo
        token = self._cache.get(self._cache_key())
        if token is None or self._is_expired(token):
            return None
        self._memo = token
        return token

    def _is_expired(self, token: CachedToken) -> bool:
        return token.expires_at <= self._clock() + _EXPIRY_SKEW_SECONDS

    def _mint(self, client: httpx.Client) -> CachedToken:
        response = client.post(
            self._config.token_url,
            data=self._token_form(),
            headers={"Accept": "application/json"},
            timeout=self._config.timeout,
        )
        return self._cache_response(response)

    async def _mint_async(self, client: httpx.AsyncClient) -> CachedToken:
        response = await client.post(
            self._config.token_url,
            data=self._token_form(),
            headers={"Accept": "application/json"},
            timeout=self._config.timeout,
        )
        return self._cache_response(response)

    def _cache_response(self, response: httpx.Response) -> CachedToken:
        if response.status_code >= 400:
            raise DhlAuthError(f"DHL token request returned HTTP {response.status_code}")
        try:
            from dhlkit.generated.models.auth import TokenResponse

            payload = TokenResponse.model_validate(orjson.loads(response.content))
        except (ValueError, orjson.JSONDecodeError) as exc:
            raise DhlAuthError("DHL token response was not valid JSON") from exc
        access_token = payload.access_token
        if not access_token:
            raise DhlAuthError("DHL token response did not contain access_token")
        expires_in = payload.expires_in or 1800
        token = CachedToken(
            access_token=access_token,
            expires_at=self._clock() + float(expires_in),
        )
        self._memo = token
        self._cache.set(self._cache_key(), token)
        return token

    def _token_form(self) -> dict[str, str]:
        return {
            "grant_type": "password",
            "client_id": self._config.require_api_key(),
            "client_secret": self._config.require_api_secret(),
            "username": self._config.require_gkp_user(),
            "password": self._config.require_gkp_password(),
        }

    def _cache_key(self) -> str:
        if self._key is None:
            material = f"{self._config.token_url}\0{self._config.require_api_key()}".encode()
            self._key = hashlib.sha256(material).hexdigest()
        return self._key
