from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import httpx
import pytest

from dhlkit import DhlConfig, DhlConfigError

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def token_response() -> Callable[..., httpx.Response]:
    """Factory for the fake ROPC token endpoint reply used across the auth tests."""

    def make(access_token: str = "token", *, expires_in: int = 1800) -> httpx.Response:
        return httpx.Response(
            200,
            json={"access_token": access_token, "token_type": "Bearer", "expires_in": expires_in},
        )

    return make


@pytest.fixture
def config() -> DhlConfig:
    return DhlConfig(
        api_key="test-api-key",
        api_secret="test-api-secret",
        gkp_user="test-gkp-user",
        gkp_password="test-gkp-password",
        max_retries=0,
        retry_backoff=0,
    )


@pytest.fixture
def fixture_bytes():
    def load(name: str) -> bytes:
        return (FIXTURES / name).read_bytes()

    return load


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def pytest_runtest_setup(item: pytest.Item) -> None:
    if "live" not in item.keywords:
        return
    mark_expression = item.config.option.markexpr or ""
    if "live" not in mark_expression or "not live" in mark_expression:
        pytest.skip("live tests are opt-in with `pytest -m live`")
    if not _live_credentials_available():
        pytest.skip("live DHL credentials are not available")


def _live_credentials_available() -> bool:
    try:
        config = DhlConfig.resolve()
    except DhlConfigError:
        return False
    return all((config.api_key, config.api_secret, config.gkp_user, config.gkp_password))
