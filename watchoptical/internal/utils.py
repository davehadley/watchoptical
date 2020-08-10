import contextlib
import glob
import os
import re
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


def _expandpatterns(patterns: Iterable[str]) -> List[str]:
    return list(sorted(mapcat(_matchfilepattern, patterns)))


@curry
def _crawldirectoryforfilesmatching(pattern: str, directory: str) -> List[str]:
    if os.path.isdir(directory):
        return [expandpath(os.sep.join((root, fname)))
                for root, dirs, files in os.walk(directory)
                for fname in files if re.match(pattern, fname)]
    else:
        return [directory] if re.match(pattern, directory) else []


def findfiles(patterns: Iterable[str]) -> List[str]:
    return list(sorted(mapcat(_matchfilepattern, patterns)))


def searchdirectories(filepattern: str, directories: Iterable[str]) -> List[str]:
    """Search directories for files matching filepattern regex."""
    return list(sorted(mapcat(_crawldirectoryforfilesmatching(filepattern), findfiles(directories))))


def searchforrootfilesexcludinganalysisfiles(directories: Iterable[str]):
    return searchdirectories(r"^(?!watchopticalanalysis).*.root$", directories)


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
