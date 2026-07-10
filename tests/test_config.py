from __future__ import annotations

import json

import pytest

from dhlkit import DhlConfig, DhlConfigError


def test_config_loads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DHL_API_KEY", "key")
    monkeypatch.setenv("DHL_API_SECRET", "secret")
    monkeypatch.setenv("DHL_GKP_USER", "user")
    monkeypatch.setenv("DHL_GKP_PASSWORD", "password")
    monkeypatch.setenv("DHL_SANDBOX", "true")

    config = DhlConfig.from_env()

    assert config.require_api_key() == "key"
    assert config.sandbox is True
    assert config.pickup_url.startswith("https://api-sandbox.dhl.com/")


def test_config_loads_protected_file(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "api_key": "key",
                "api_secret": "secret",
                "gkp_user": "user",
                "gkp_password": "password",
            }
        )
    )
    path.chmod(0o600)

    config = DhlConfig.from_file(path)

    assert config.require_gkp_user() == "user"


def test_config_rejects_permissive_file(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{}")
    path.chmod(0o644)

    with pytest.raises(DhlConfigError, match="0600"):
        DhlConfig.from_file(path)


def test_config_rejects_unknown_file_fields(tmp_path) -> None:
    path = tmp_path / "config.json"
    path.write_text('{"api_keey":"typo"}')
    path.chmod(0o600)

    with pytest.raises(DhlConfigError, match="api_keey"):
        DhlConfig.from_file(path)


def test_missing_secret_names_environment_variable(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    monkeypatch.delenv("DHL_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(DhlConfigError, match="DHL_API_KEY"):
        DhlConfig().require_api_key()


def _write_credential_file(path, api_key: str) -> None:
    path.write_text(
        json.dumps(
            {
                "api_key": api_key,
                "api_secret": "secret",
                "gkp_user": "user",
                "gkp_password": "password",
            }
        )
    )
    path.chmod(0o600)


def test_resolve_prefers_complete_environment(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)  # avoid a repo-local .env
    monkeypatch.setenv("DHL_API_KEY", "env-key")
    monkeypatch.setenv("DHL_API_SECRET", "secret")
    monkeypatch.setenv("DHL_GKP_USER", "user")
    monkeypatch.setenv("DHL_GKP_PASSWORD", "password")
    path = tmp_path / "config.json"
    _write_credential_file(path, api_key="file-key")

    config = DhlConfig.resolve(path)

    assert config.require_api_key() == "env-key"  # complete env wins over the file


def test_resolve_falls_back_to_file_when_env_incomplete(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    monkeypatch.chdir(tmp_path)
    for name in ("DHL_API_KEY", "DHL_API_SECRET", "DHL_GKP_USER", "DHL_GKP_PASSWORD"):
        monkeypatch.delenv(name, raising=False)
    path = tmp_path / "config.json"
    _write_credential_file(path, api_key="file-key")

    config = DhlConfig.resolve(path)

    assert config.require_api_key() == "file-key"


def test_resolve_raises_on_unreadable_file(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    for name in ("DHL_API_KEY", "DHL_API_SECRET", "DHL_GKP_USER", "DHL_GKP_PASSWORD"):
        monkeypatch.delenv(name, raising=False)
    path = tmp_path / "config.json"
    path.write_text("{}")
    path.chmod(0o644)  # a present but unreadable file must not be silently ignored

    with pytest.raises(DhlConfigError, match="0600"):
        DhlConfig.resolve(path)


def test_base_url_override_applies_to_all_resources() -> None:
    config = DhlConfig(base_url="https://example.test/")

    assert config.token_url == "https://example.test/parcel/de/account/auth/ropc/v1/token"
    assert config.legacy_tracking_url == "https://example.test/parcel/de/tracking/v0"
    assert config.unified_tracking_url == "https://example.test/track"
