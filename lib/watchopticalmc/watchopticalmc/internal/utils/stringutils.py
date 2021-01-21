import hashlib
from typing import Iterable


def hashfromstrcol(values: Iterable[str]) -> str:
    h = hashlib.md5()
    for s in values:
        h.update(s.encode())
    return h.hexdigest()
