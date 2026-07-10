from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast

import httpx
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    Retrying,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_random_exponential,
)

from .config import DhlConfig

_IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})


def should_retry_response(method: str, response: httpx.Response) -> bool:
    if response.status_code == 429:
        return True
    return response.status_code in {500, 502, 503, 504} and method.upper() in _IDEMPOTENT_METHODS


def run_with_retry(
    operation: Callable[[], httpx.Response],
    *,
    method: str,
    config: DhlConfig,
) -> httpx.Response:
    retrying = Retrying(
        stop=stop_after_attempt(config.max_retries + 1),
        wait=wait_random_exponential(
            multiplier=config.retry_backoff,
            max=config.retry_max_backoff,
        ),
        retry=retry_if_exception_type(httpx.TransportError)
        | retry_if_result(lambda response: should_retry_response(method, response)),
        retry_error_callback=_last_result_or_raise,
        reraise=True,
    )
    return retrying(operation)


async def run_with_retry_async(
    operation: Callable[[], Awaitable[httpx.Response]],
    *,
    method: str,
    config: DhlConfig,
) -> httpx.Response:
    retrying = AsyncRetrying(
        stop=stop_after_attempt(config.max_retries + 1),
        wait=wait_random_exponential(
            multiplier=config.retry_backoff,
            max=config.retry_max_backoff,
        ),
        retry=retry_if_exception_type(httpx.TransportError)
        | retry_if_result(lambda response: should_retry_response(method, response)),
        retry_error_callback=_last_result_or_raise,
        reraise=True,
    )
    return cast(httpx.Response, await retrying(operation))


def _last_result_or_raise(state: RetryCallState) -> object:
    outcome = state.outcome
    if outcome is None:
        raise RuntimeError("retry completed without an outcome")
    if outcome.failed:
        exception = outcome.exception()
        if exception is None:
            raise RuntimeError("retry failed without an exception")
        raise exception
    return outcome.result()
