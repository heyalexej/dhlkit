from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .client import DhlClient
from .config import DhlConfig
from .unified import track as normalized_track

app = typer.Typer(help="Typed DHL Parcel DE command-line client")
console = Console()


@app.command("pickup-locations")
def pickup_locations(
    postal_code: Annotated[str | None, typer.Option(help="Optional postal-code filter")] = None,
) -> None:
    """List agreed pickup locations."""
    with DhlClient(_config()) as dhl:
        locations = dhl.pickup.locations(postal_code=postal_code)
    table = Table("AS ID", "City", "Postal code")
    for location in locations:
        address = location.pickup_address
        table.add_row(
            str(location.id.root) if location.id else "",
            str(address.city.root) if address and address.city else "",
            str(address.postal_code.root) if address and address.postal_code else "",
        )
    console.print(table)


@app.command("postnumber")
def postnumber(postnumber: str, firstname: str, lastname: str) -> None:
    """Verify a postnumber and customer name."""
    with DhlClient(_config()) as dhl:
        result = dhl.postnumber.verify(postnumber, firstname=firstname, lastname=lastname)
    console.print_json(data=result.model_dump(mode="json", by_alias=True))


@app.command("track")
def track(tracking_number: str, unified: bool = False) -> None:
    """Track one shipment and print a normalized, secret-free result."""
    with DhlClient(_config()) as dhl:
        result = normalized_track(
            dhl,
            tracking_number,
            prefer="unified" if unified else "legacy",
        )
    console.print_json(data=result.model_dump(mode="json", by_alias=True))


def _config() -> DhlConfig:
    return DhlConfig.resolve()


if __name__ == "__main__":
    app()
