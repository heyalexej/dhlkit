from __future__ import annotations

from gen_models import ROOT, _model_only_spec, _resolve_enum_repr_defaults

from dhlkit.generated.models.tracking_unified import (
    Company,
    Organization,
    Person,
    TrackingShipments,
)


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


def test_resolve_enum_repr_defaults_rewrites_member_repr_to_wire_value() -> None:
    source = (
        "class SecretPolicy(RootModel[Literal['none', 'postal-code']]):\n"
        "    root: Literal['none', 'postal-code']\n"
        "policy: SecretPolicy = 'SecretPolicy.POSTAL_CODE'\n"
        "url: str = 'example.com'\n"
    )

    resolved = _resolve_enum_repr_defaults(source)

    assert "policy: SecretPolicy = 'postal-code'" in resolved
    assert "SecretPolicy.POSTAL_CODE" not in resolved
    assert "url: str = 'example.com'" in resolved  # non-enum reprs are left untouched


def test_secret_policy_defaults_are_valid_wire_values() -> None:
    # Regression: datamodel-code-generator emitted the default as the member repr
    # ('SecretPolicy.POSTAL_CODE'), which failed the field's validate_default check
    # and made every named party entity unconstructable.
    for entity in (Person, Organization, Company):
        policy = entity().field_policy
        assert policy is not None
        assert policy.root == "postal-code"


def test_shipment_with_named_parties_parses() -> None:
    payload = {
        "shipments": [
            {
                "id": "00340434780401935421",
                "service": "parcel-de",
                "status": {
                    "statusCode": "transit",
                    "status": "EE",
                    "description": "in transit",
                    "timestamp": "2026-07-09T06:01:00",
                },
                "details": {
                    "sender": {"@type": "Person", "givenName": "Max", "familyName": "M"},
                    "receiver": {"@type": "Organization", "organizationName": "ACME GmbH"},
                },
            }
        ]
    }

    shipments = TrackingShipments.model_validate(payload).shipments
    assert shipments is not None
    details = shipments[0].details
    assert details is not None
    assert details.sender is not None
    assert details.receiver is not None
    assert isinstance(details.sender.root, Person)
    assert isinstance(details.receiver.root, Organization)
