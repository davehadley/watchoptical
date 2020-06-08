import glob
from os.path import expanduser, expandvars, abspath
from pathlib import Path
from typing import Iterable, List, Callable, Any, Tuple

from toolz import pipe
from toolz import mapcat, curry


def _matchfilepattern(pattern: str) -> List[str]:
    return pipe(pattern, expanduser, expandvars, abspath, glob.glob)


def findfiles(patterns: Iterable[str]) -> List[str]:
    return list(sorted(mapcat(_matchfilepattern, patterns)))

def touchfile(path:str)->None:
    return Path(path).touch()