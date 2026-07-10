from __future__ import annotations

import os
from pathlib import Path

import pytest

from dhlkit import DhlClient, DhlConfig

pytestmark = pytest.mark.live


@pytest.fixture
def live_config() -> DhlConfig:
    if all(os.getenv(name) for name in _credential_names()):
        return DhlConfig.from_env()
    return DhlConfig.from_file()


@pytest.fixture
def live_client(live_config: DhlConfig):
    with DhlClient(live_config) as client:
        yield client


def test_live_pickup_locations(live_client: DhlClient) -> None:
    locations = live_client.pickup.locations()

    assert isinstance(locations, list)


def test_live_postnumber(live_client: DhlClient) -> None:
    result = live_client.postnumber.verify(
        "871902603",
        firstname="Max",
        lastname="Mustermann",
    )

    assert isinstance(result.valid, bool)


def test_live_legacy_tracking_batch(live_client: DhlClient) -> None:
    numbers = _tracking_numbers()[:15]

    result = live_client.tracking.legacy(numbers)

    assert result.code == "0"
    assert isinstance(result.shipments, list)


def test_live_unified_tracking_sample(live_client: DhlClient) -> None:
    successes = 0
    for number in _tracking_numbers()[:8]:
        result = live_client.tracking.unified(number)
        if result.shipments:
            successes += 1

    assert successes >= 1


def _tracking_numbers() -> list[str]:
    path_value = os.getenv("DHLKIT_TRACKING_NUMBERS_FILE")
    if path_value:
        path = Path(path_value).expanduser()
        numbers = [line.strip() for line in path.read_text().splitlines() if line.strip()]
        if numbers:
            return numbers
    return ["00340434780401935407"]


def _credential_names() -> tuple[str, ...]:
    return (
        "DHL_API_KEY",
        "DHL_API_SECRET",
        "DHL_GKP_USER",
        "DHL_GKP_PASSWORD",
    )
