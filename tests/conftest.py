from __future__ import annotations

import os
from pathlib import Path

import pytest

from dhlkit import DhlConfig

FIXTURES = Path(__file__).parent / "fixtures"


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
    if all(os.getenv(name) for name in _credential_names()):
        return True
    try:
        config = DhlConfig.from_file()
    except Exception:
        return False
    return all((config.api_key, config.api_secret, config.gkp_user, config.gkp_password))


def _credential_names() -> tuple[str, ...]:
    return (
        "DHL_API_KEY",
        "DHL_API_SECRET",
        "DHL_GKP_USER",
        "DHL_GKP_PASSWORD",
    )
