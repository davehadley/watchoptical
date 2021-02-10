from contextlib import AbstractContextManager
from typing import Any, Callable, MutableMapping

import cloudpickle
from sqlitedict import SqliteDict

DEFAULT_DBNAME = "watchoptical_cache.db"


def cacheget(key: str, dbname: str = DEFAULT_DBNAME) -> Any:
    with Cache(dbname) as db:
        return db[key]


def cachedcall(
    key: str,
    f: Callable,
    *args,
    dbname: str = DEFAULT_DBNAME,
    forcecall: bool = False,
    **kwargs,
) -> Any:
    with Cache(dbname) as db:
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


class Cache(AbstractContextManager):
    def __init__(self, dbname=DEFAULT_DBNAME):
        self._dbname = dbname
        self._backing = None

    def __enter__(self) -> MutableMapping[str, Any]:
        self._backing = SqliteDict(
            self._dbname,
            autocommit=True,
            encode=cloudpickle.dumps,
            decode=cloudpickle.loads,
        )
        return self._backing.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        self._backing.__exit__(exc_type, exc_value, traceback)
        del self._backing
