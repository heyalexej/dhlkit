#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["dhlkit"]
# ///
"""Select rich live tracking histories and write aggressively sanitized fixtures.

The input files contain one tracking number per line. Output never contains a real
tracking number, request/piece ID, reference, person, street, postal code, email, phone,
or event location. Console output is aggregate-only.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree

import httpx

from dhlkit import DhlClient, DhlConfig, DhlError
from dhlkit.auth import BasicKeySecretAuth
from dhlkit.resources.tracking_legacy import (
    LegacyShipment,
    LegacyTrackingEvent,
    _request_xml,
)

FAKE_TRACKING_NUMBER = "00340434123456789012"
RETURN_SIGNALS = (
    "nicht abgeholt",
    "nicht angetroffen",
    "zurück",
    "retour",
    "return",
    "abhol",
    "filiale",
    "pickup",
    "customs",
    "zustellversuch",
    "lagerfrist",
    "rücksend",
    "return to sender",
    "not collected",
    "unclaimed",
)
STRONG_RETURN_SIGNALS = (
    "nicht abgeholt",
    "lagerfrist",
    "zurück an den absender",
    "an den absender zurück",
    "return to sender",
    "not collected",
    "unclaimed",
)


def main() -> None:
    args = _parser().parse_args()
    numbers = _numbers(args.tracking_file, args.foreign_file)
    if not numbers:
        raise SystemExit("No tracking numbers were provided")

    config = _config()
    shipments: list[LegacyShipment] = []
    print(f"Live fixture scan: 0/{len(numbers)}", flush=True)
    with DhlClient(config) as client:
        for start in range(0, len(numbers), 15):
            batch = numbers[start : start + 15]
            result = client.tracking.legacy(batch)
            shipments.extend(result.shipments)
            print(f"Live fixture scan: {min(start + 15, len(numbers))}/{len(numbers)}", flush=True)
        if not shipments:
            raise SystemExit("DHL returned no legacy shipments")
        selected = max(shipments, key=_score)
        if not any(shipment.events for shipment in shipments):
            _diagnose_live_shape(config, numbers[:1])
        _write_legacy(args.legacy_output, selected)
        try:
            unified = client.tracking.unified(selected.piece_code or selected.searched_piece_code)
        except DhlError:
            print("Unified fixture: unavailable for selected sample", flush=True)
        else:
            _write_unified(args.unified_output, unified)
            print("Unified fixture: sanitized", flush=True)

    signal_count = sum(_signal_count(shipment) > 0 for shipment in shipments)
    strong_count = sum(_strong_return(shipment) for shipment in shipments)
    print(
        f"Live fixture scan complete: {len(shipments)} results, "
        f"{signal_count} return-like histories, {strong_count} uncollected/return histories, "
        f"selected {len(selected.events)} events",
        flush=True,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("tracking_file", type=Path)
    parser.add_argument("--foreign-file", type=Path)
    parser.add_argument("--legacy-output", type=Path, required=True)
    parser.add_argument("--unified-output", type=Path, required=True)
    return parser


def _config() -> DhlConfig:
    return DhlConfig.resolve()


def _numbers(primary: Path, foreign: Path | None) -> list[str]:
    values: list[str] = []
    for path in (primary, foreign):
        if path is None:
            continue
        values.extend(line.strip() for line in path.read_text().splitlines() if line.strip())
    return list(dict.fromkeys(values))


def _score(shipment: LegacyShipment) -> int:
    return len(shipment.events) + _signal_count(shipment) * 20 + _strong_return(shipment) * 200


def _signal_count(shipment: LegacyShipment) -> int:
    text = _history_text(shipment)
    return sum(signal in text for signal in RETURN_SIGNALS)


def _strong_return(shipment: LegacyShipment) -> bool:
    text = _history_text(shipment)
    return any(signal in text for signal in STRONG_RETURN_SIGNALS)


def _history_text(shipment: LegacyShipment) -> str:
    return " ".join(
        filter(
            None,
            [
                shipment.status,
                shipment.short_status,
                *(event.status for event in shipment.events),
                *(event.text for event in shipment.events),
            ],
        )
    ).lower()


def _write_legacy(path: Path, shipment: LegacyShipment) -> None:
    root = ElementTree.Element(
        "data",
        {"name": "pieceshipmentlist", "request-id": "fixture-return-history", "code": "0"},
    )
    shipment_element = ElementTree.SubElement(
        root,
        "data",
        {
            "name": "pieceshipment",
            "error-status": shipment.error_status or "0",
            "piece-id": "fixture-piece-return",
            "piece-identifier": "340434123456789012",
            "piece-code": FAKE_TRACKING_NUMBER,
            "searched-piece-code": FAKE_TRACKING_NUMBER,
            "status-timestamp": _legacy_time(max(len(shipment.events) - 1, 0)),
            "status": _safe_text(shipment.status) or "Shipment history complete.",
            "short-status": _safe_text(shipment.short_status) or "History complete",
            "product-name": _safe_text(shipment.product_name) or "DHL PAKET",
            "delivery-event-flag": "1" if shipment.delivered else "0",
            "ruecksendung": "true" if shipment.returned else "false",
        },
    )
    event_list = ElementTree.SubElement(
        shipment_element,
        "data",
        {
            "name": "pieceeventlist",
            "piece-id": "fixture-piece-return",
            "piece-identifier": "340434123456789012",
        },
    )
    for index, event in enumerate(shipment.events):
        ElementTree.SubElement(event_list, "data", _legacy_event(index, event))
    ElementTree.indent(root, space="  ")
    rendered = ElementTree.tostring(root, encoding="unicode", xml_declaration=False)
    _write_private(path, f'<?xml version="1.0" encoding="UTF-8"?>\n{rendered}\n')


def _legacy_event(index: int, event: LegacyTrackingEvent) -> dict[str, str]:
    values = {
        "name": "pieceevent",
        "event-timestamp": _legacy_time(index),
        "event-status": _safe_text(event.status or event.text) or "Shipment event",
        "event-text": _safe_text(event.text or event.status) or "Shipment event",
        "event-short-status": _safe_text(event.short_status) or "Shipment event",
        "ice": event.ice or "",
        "ric": event.ric or "",
        "event-location": f"Example Hub {index + 1}",
        "event-country": "Example Country",
        "standard-event-code": event.standard_event_code or "",
    }
    return {key: value for key, value in values.items() if value}


def _legacy_time(index: int) -> str:
    timestamp = datetime(2026, 1, 2, 8, tzinfo=UTC) + timedelta(hours=index * 8)
    return timestamp.strftime("%d.%m.%Y %H:%M")


def _write_unified(path: Path, result: object) -> None:
    shipments = getattr(result, "shipments", None) or []
    if not shipments:
        return
    shipment = shipments[0]
    status = shipment.status
    details = shipment.details
    product = details.product if details else None
    payload = {
        "shipments": [
            {
                "id": FAKE_TRACKING_NUMBER,
                "service": shipment.service.root if shipment.service else "parcel-de",
                "origin": _country_place(shipment.origin),
                "destination": _country_place(shipment.destination),
                "status": _unified_status(status, len(shipment.events or [])),
                "returnFlag": shipment.return_flag.root if shipment.return_flag else False,
                "details": {
                    "product": {"productName": _safe_text(product.product_name)}
                    if product and product.product_name
                    else None,
                    "totalNumberOfPieces": details.total_number_of_pieces if details else None,
                },
                "events": [
                    _unified_status(event, index)
                    for index, event in enumerate(shipment.events or [])
                ],
            }
        ]
    }
    _drop_none(payload)
    _write_private(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def _unified_status(status: object, index: int) -> dict[str, object]:
    return {
        "timestamp": (datetime(2026, 1, 2, 8, tzinfo=UTC) + timedelta(hours=index * 8)).isoformat(),
        "statusCode": getattr(getattr(status, "status_code", None), "root", "unknown"),
        "status": _safe_text(getattr(status, "status", None)),
        "statusDetailed": _safe_text(getattr(status, "status_detailed", None)),
        "description": _safe_text(getattr(status, "description", None)),
        "remark": _safe_text(getattr(status, "remark", None)),
        "location": {"address": {"addressLocality": f"Example Hub {index + 1}"}},
    }


def _country_place(place: object) -> dict[str, object] | None:
    address = getattr(place, "address", None)
    country = getattr(getattr(address, "country_code", None), "root", None)
    return {"address": {"countryCode": country}} if country else None


def _drop_none(value: object) -> None:
    if isinstance(value, dict):
        for key in list(value):
            item = value[key]
            if item is None:
                del value[key]
            else:
                _drop_none(item)
    elif isinstance(value, list):
        for item in value:
            _drop_none(item)


def _safe_text(value: str | None) -> str | None:
    if not value:
        return value
    text = html.unescape(value)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"https?://\S+", "https://example.invalid/tracking", text)
    text = re.sub(
        r"\b(?=[A-Z0-9]{8,30}\b)(?=[A-Z0-9]*\d)[A-Z0-9]+\b",
        "SANITIZED-ID",
        text,
        flags=re.IGNORECASE,
    )
    return text.strip()


def _write_private(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(0o600)


def _diagnose_live_shape(config: DhlConfig, numbers: list[str]) -> None:
    xml = _request_xml(
        config,
        numbers,
        customer_references=None,
        postal_code=None,
        language="de",
        from_date=None,
        to_date=None,
    )
    with httpx.Client(timeout=config.timeout) as client:
        headers = BasicKeySecretAuth(config).headers(client)
        response = client.get(
            f"{config.legacy_tracking_url}/shipments",
            params={"xml": xml},
            headers=headers,
        )
        response.raise_for_status()
    root = ElementTree.fromstring(response.content)
    names = Counter(child.attrib.get("name", "<none>") for child in root)
    relationships = Counter(
        (child.attrib.get("name", "<none>"), grandchild.attrib.get("name", "<none>"))
        for child in root
        for grandchild in child
    )
    attributes = {child.attrib.get("name", "<none>"): sorted(child.attrib) for child in root}
    print(f"Live XML child types: {dict(names)}", flush=True)
    print(f"Live XML nesting: {dict(relationships)}", flush=True)
    print(f"Live XML attribute names: {attributes}", flush=True)


if __name__ == "__main__":
    main()
