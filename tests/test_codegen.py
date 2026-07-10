from __future__ import annotations

from dhlkit._gen import ROOT, _model_only_spec


def test_codegen_discards_spec_auth_declarations() -> None:
    document = _model_only_spec(ROOT / "specs" / "postnumber-v1.yaml")

    assert "security" not in document
    assert "securitySchemes" not in document["components"]
    assert "security" not in document["paths"]["/customers/{postnumber}"]["post"]


def test_generated_files_have_warning_banner() -> None:
    generated = ROOT / "src" / "dhlkit" / "generated" / "models"

    for path in generated.glob("*.py"):
        if path.name != "__init__.py":
            assert "DO NOT EDIT" in path.read_text().splitlines()[0]
