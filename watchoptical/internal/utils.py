import contextlib
import functools
import glob
import hashlib
import operator
import os
import re
import shelve
from os.path import abspath, expanduser, expandvars
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable, Iterable, List, MutableMapping

from toolz import curry, mapcat, merge_with, pipe


def expandpath(path):
    return pipe(path, expanduser, expandvars, abspath)


def _matchfilepattern(pattern: str) -> List[str]:
    return pipe(pattern, expandpath, glob.glob)


def _expandpatterns(patterns: Iterable[str]) -> List[str]:
    return list(sorted(mapcat(_matchfilepattern, patterns)))


@curry
def _crawldirectoryforfilesmatching(pattern: str, directory: str) -> List[str]:
    if os.path.isdir(directory):
        return [
            expandpath(os.sep.join((root, fname)))
            for root, dirs, files in os.walk(directory)
            for fname in files
            if re.match(pattern, fname)
        ]
    else:
        return [directory] if re.match(pattern, directory) else []


def findfiles(patterns: Iterable[str]) -> List[str]:
    return list(sorted(mapcat(_matchfilepattern, patterns)))


def searchdirectories(filepattern: str, directories: Iterable[str]) -> List[str]:
    """Search directories for files matching filepattern regex."""
    return list(
        sorted(
            mapcat(_crawldirectoryforfilesmatching(filepattern), findfiles(directories))
        )
    )


def searchforrootfilesexcludinganalysisfiles(directories: Iterable[str]):
    return searchdirectories(
        r"^(?!watchopticalanalysis|merged|analysis|results).*.root$", directories
    )


def touchfile(path: str) -> None:
    return Path(path).touch()


@contextlib.contextmanager
def temporaryworkingdirectory() -> str:
    cwd = os.getcwd()
    try:
        with TemporaryDirectory() as d:
            os.chdir(d)
            yield d
    finally:
        os.chdir(cwd)


def hashfromstrcol(values: Iterable[str]) -> str:
    h = hashlib.md5()
    for s in values:
        h.update(s.encode())
    return h.hexdigest()


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


def sumlist(iterable: Iterable[Any]):
    return functools.reduce(operator.add, iterable)


def summap(
    iterable: Iterable[MutableMapping[Any, Any]], add: Callable = operator.add
) -> MutableMapping[Any, Any]:
    sum = functools.partial(functools.reduce, add)
    return functools.reduce(functools.partial(merge_with, sum), iterable)
