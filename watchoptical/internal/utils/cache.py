import shelve
from typing import Callable

DEFAULT_DBNAME = "watchoptical.shelve.db"


def shelvedget(key: str, dbname: str = DEFAULT_DBNAME):
    with shelve.open(dbname) as db:
        return db[key]


def shelvedcall(
    key: str,
    f: Callable,
    *args,
    dbname: str = DEFAULT_DBNAME,
    forcecall: bool = False,
    **kwargs,
):
    with shelve.open(dbname) as db:
        if key in db and not forcecall:
            return db[key]
        else:
            result = f(*args, **kwargs)
            db[key] = result
            return result


def shelveddecorator(keyfunc: Callable, dbname: str = DEFAULT_DBNAME):
    def g(f: Callable):
        def h(*args, forcecall: bool = False, **kwargs):
            key = keyfunc(*args, **kwargs)
            return shelvedcall(
                key, f, *args, dbname=dbname, forcecall=forcecall, **kwargs
            )

        return h

    return g
