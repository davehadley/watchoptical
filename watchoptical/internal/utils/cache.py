import shelve
from typing import Any, Callable

DEFAULT_DBNAME = "watchoptical_cache.db"


def cacheget(key: str, dbname: str = DEFAULT_DBNAME) -> Any:
    with shelve.open(dbname) as db:
        return db[key]


def cachedcall(
    key: str,
    f: Callable,
    *args,
    dbname: str = DEFAULT_DBNAME,
    forcecall: bool = False,
    **kwargs,
) -> Any:
    with shelve.open(dbname) as db:
        if key in db and not forcecall:
            return db[key]
        else:
            result = f(*args, **kwargs)
            db[key] = result
            return result


def cachedcallable(keyfunc: Callable, dbname: str = DEFAULT_DBNAME) -> Callable:
    def g(f: Callable):
        def h(*args, forcecall: bool = False, **kwargs):
            key = keyfunc(*args, **kwargs)
            return cachedcall(
                key, f, *args, dbname=dbname, forcecall=forcecall, **kwargs
            )

        return h

    return g
