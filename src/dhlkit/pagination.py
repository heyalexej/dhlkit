from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import Any
from urllib.parse import parse_qs, urlsplit

from pydantic import BaseModel


def paginate(
    method: Callable[..., Any],
    *args: Any,
    items_field: str,
    max_items: int | None = None,
    **kwargs: Any,
) -> Iterator[Any]:
    """Yield ``items_field`` entries across offset-based pages until ``nextUrl`` is absent.

    ``items_field`` is required: it names the list attribute on each page (for
    Unified Tracking that is ``"shipments"``) and has no endpoint-specific default,
    so a wrong field fails loudly rather than yielding nothing.
    """
    yielded = 0
    while True:
        page = method(*args, **kwargs)
        items = _items(page, items_field)
        for item in items:
            yield item
            yielded += 1
            if max_items is not None and yielded >= max_items:
                return
        if not items or not _advance(page, kwargs):
            return


async def paginate_async(
    method: Callable[..., Awaitable[Any]],
    *args: Any,
    items_field: str,
    max_items: int | None = None,
    **kwargs: Any,
) -> AsyncIterator[Any]:
    """Asynchronous counterpart of :func:`paginate`; ``items_field`` is required."""
    yielded = 0
    while True:
        page = await method(*args, **kwargs)
        items = _items(page, items_field)
        for item in items:
            yield item
            yielded += 1
            if max_items is not None and yielded >= max_items:
                return
        if not items or not _advance(page, kwargs):
            return


def _items(page: Any, field: str) -> list[Any]:
    if isinstance(page, BaseModel):
        value = getattr(page, field, None)
    elif isinstance(page, dict):
        value = page.get(field)
    else:
        value = None
    return value if isinstance(value, list) else []


def _advance(page: Any, kwargs: dict[str, Any]) -> bool:
    next_url = getattr(page, "next_url", None)
    if next_url is None and isinstance(page, dict):
        next_url = page.get("nextUrl")
    if not next_url:
        return False
    query = parse_qs(urlsplit(str(next_url)).query)
    update = {key: values[0] for key, values in query.items() if key in {"offset", "limit"}}
    if not update or update.get("offset") == str(kwargs.get("offset")):
        return False
    kwargs.update(update)
    return True
