from contextlib import AbstractContextManager
from typing import Any, Callable, Iterator, MutableMapping

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


class Cache(MutableMapping[str, Any], AbstractContextManager):
    def __init__(self, dbname=DEFAULT_DBNAME):
        self._backing = SqliteDict(
            dbname,
            autocommit=True,
            encode=cloudpickle.dumps,
            decode=cloudpickle.loads,
        )

    def __setitem__(self, k: str, v: Any) -> None:
        self._backing[k] = v

    def __delitem__(self, k: str) -> None:
        del self._backing[k]

    def __getitem__(self, k: str) -> Any:
        return self._backing[k]

    def __len__(self) -> int:
        return len(self._backing)

    def __iter__(self) -> Iterator[str]:
        return iter(self._backing)

    def __enter__(self):
        self._backing.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._backing.__exit__()
