from typing import Callable


def retry(n: int) -> Callable:
    def decorator(f: Callable) -> Callable:
        def fprime(*args, **kwargs):
            reraise = ValueError("retry number must 1 or greater.")
            for _ in range(max(1, n)):
                try:
                    return f(*args, **kwargs)
                except Exception as ex:
                    reraise = ex
            # re-raise if we make it here Exception
            raise reraise

        return fprime

    return decorator
