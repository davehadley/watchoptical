import contextlib
import glob
import os
from os.path import expanduser, expandvars, abspath
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable, List, Callable, Any, Tuple

from toolz import pipe
from toolz import mapcat, curry


def expandpath(path):
    return pipe(path, expanduser, expandvars, abspath)


def _matchfilepattern(pattern: str) -> List[str]:
    return pipe(pattern, expandpath, glob.glob)


def findfiles(patterns: Iterable[str]) -> List[str]:
    return list(sorted(mapcat(_matchfilepattern, patterns)))


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