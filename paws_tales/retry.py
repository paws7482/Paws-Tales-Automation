from __future__ import annotations

import random
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    attempts: int
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0
    jitter_seconds: float = 0.25

    def validate(self) -> None:
        if self.attempts < 1:
            raise ValueError("Retry attempts must be at least 1.")
        if self.base_delay_seconds < 0 or self.max_delay_seconds < self.base_delay_seconds:
            raise ValueError("Retry delay configuration is invalid.")


def run_with_retries(
    operation: Callable[[], T],
    policy: RetryPolicy,
    retryable_exceptions: Iterable[type[BaseException]],
    retryable_statuses: set[int] | None = None,
    status_getter: Callable[[BaseException], int | None] | None = None,
) -> T:
    policy.validate()
    retryable = tuple(retryable_exceptions)
    last_error: BaseException | None = None
    for attempt in range(1, policy.attempts + 1):
        try:
            return operation()
        except retryable as exc:
            last_error = exc
            status = status_getter(exc) if status_getter else None
            if retryable_statuses is not None and status not in retryable_statuses:
                raise
            if attempt == policy.attempts:
                raise
            delay = min(policy.base_delay_seconds * (2 ** (attempt - 1)), policy.max_delay_seconds)
            if policy.jitter_seconds:
                delay += random.uniform(0, policy.jitter_seconds)
            time.sleep(delay)
    raise RuntimeError("Retry operation did not complete.") from last_error
