import time
from collections.abc import Callable
from functools import wraps
from typing import Any


def retry(max_attempts: int = 3, delay: int = 2):
    """Повторяет функцию при ошибке."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise last_exception

        return wrapper

    return decorator
