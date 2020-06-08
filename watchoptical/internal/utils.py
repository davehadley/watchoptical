import glob
from os.path import expanduser, expandvars, abspath
from typing import Iterable, List

from toolz import pipe
from toolz import mapcat


def _matchfilepattern(pattern: str) -> List[str]:
    return pipe(pattern, expanduser, expandvars, abspath, glob.glob)


def findfiles(patterns: Iterable[str]) -> List[str]:
    return list(sorted(mapcat(_matchfilepattern, patterns)))
