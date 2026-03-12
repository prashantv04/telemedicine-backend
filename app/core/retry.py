import time
from typing import Callable

from fastapi import HTTPException


def retry_with_backoff(
    operation: Callable,
    retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0
):
    """
    Retry an operation with exponential backoff.

    Example delays:
    1s → 2s → 4s
    """

    delay = initial_delay

    for attempt in range(retries):
        try:
            return operation()

        except HTTPException:
            # business errors should NOT retry
            raise

        except Exception as exc:
            if attempt == retries - 1:
                raise exc

            time.sleep(delay)
            delay *= backoff_factor