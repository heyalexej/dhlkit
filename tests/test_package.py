from __future__ import annotations

import dhlkit


def test_public_api_exports() -> None:
    expected = {
        "AsyncDhlClient",
        "DhlClient",
        "DhlConfig",
        "DhlError",
        "FileTokenCache",
        "InMemoryTokenCache",
        "TokenCache",
        "paginate",
    }

    assert expected <= set(dhlkit.__all__)
