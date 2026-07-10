from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
SPECS = {
    "auth-ropc.yaml": "auth.py",
    "pickup-v3.yaml": "pickup.py",
    "postnumber-v1.yaml": "postnumber.py",
    "track-unified.yaml": "tracking_unified.py",
}
GENERATED = ROOT / "src" / "dhlkit" / "generated" / "models"
HEADER = "# Generated from an official DHL OpenAPI document. DO NOT EDIT."


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate dhlkit's Pydantic models")
    parser.add_argument("--check", action="store_true", help="fail if generated files drift")
    args = parser.parse_args()

    executable = shutil.which("datamodel-codegen")
    if executable is None:
        raise SystemExit("datamodel-codegen is not installed; run `uv sync --dev`")

    changed: list[str] = []
    with tempfile.TemporaryDirectory(prefix="dhlkit-gen-") as temporary:
        temp_root = Path(temporary)
        for index, (spec_name, output_name) in enumerate(SPECS.items(), start=1):
            print(f"Generating models: {index}/{len(SPECS)} {spec_name}", flush=True)
            sanitized = temp_root / spec_name
            sanitized.write_text(
                json.dumps(_model_only_spec(ROOT / "specs" / spec_name)),
                encoding="utf-8",
            )
            generated = temp_root / output_name
            subprocess.run(
                [
                    executable,
                    "--input",
                    str(sanitized),
                    "--input-file-type",
                    "openapi",
                    "--output",
                    str(generated),
                    "--output-model-type",
                    "pydantic_v2.BaseModel",
                    "--target-python-version",
                    "3.12",
                    "--base-class",
                    "dhlkit.models.DhlModel",
                    "--snake-case-field",
                    "--use-standard-collections",
                    "--use-union-operator",
                    "--use-annotated",
                    "--field-constraints",
                    "--use-default",
                    "--enum-field-as-literal",
                    "all",
                    "--disable-timestamp",
                    "--custom-file-header",
                    HEADER,
                ],
                check=True,
            )
            destination = GENERATED / output_name
            current = destination.read_text(encoding="utf-8") if destination.exists() else None
            rendered = generated.read_text(encoding="utf-8")
            if current != rendered:
                changed.append(output_name)
                if not args.check:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_text(rendered, encoding="utf-8")

    if args.check and changed:
        raise SystemExit(f"Generated models are stale: {', '.join(changed)}")
    status = "up to date" if not changed else f"updated {', '.join(changed)}"
    print(f"Generated models: {status}", flush=True)


def _model_only_spec(path: Path) -> dict[str, Any]:
    """Remove security declarations; DHL specs are model inputs, never auth inputs."""
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"OpenAPI document is not an object: {path}")
    payload.pop("security", None)
    components = payload.get("components")
    if isinstance(components, dict):
        components.pop("securitySchemes", None)
    paths = payload.get("paths")
    if isinstance(paths, dict):
        for path_item in paths.values():
            if not isinstance(path_item, dict):
                continue
            for operation in path_item.values():
                if isinstance(operation, dict):
                    operation.pop("security", None)
    return payload


if __name__ == "__main__":
    main()
