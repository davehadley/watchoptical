from contextlib import suppress
from typing import Callable


def ignoreerrors(func: Callable) -> Callable:
    """If enclosed function raises any Exception, it is caught and None is returned."""

    def wrap(*args, **kwargs):
        with suppress(Exception):
            return func(*args, **kwargs)

    return wrap
