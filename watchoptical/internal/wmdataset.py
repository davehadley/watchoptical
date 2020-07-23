import itertools
import os
import re
from typing import Iterable, NamedTuple, Iterator, Tuple

from toolz import pipe, groupby

from watchoptical.internal.utils import findfiles


class RatPacBonsaiPair(NamedTuple):
    g4file: str
    bonsaifile: str

    @property
    def eventtype(self) -> str:
        return re.match(f".*Watchman_(.*){os.sep}.*.root$", self.g4file).group(1)


class WatchmanDataset:
    def __init__(self, filepatterns: Iterable[str]):
        self._files: Tuple[RatPacBonsaiPair] = pipe(filepatterns,
                          findfiles,
                          self._match_bonsai_and_ratpac,
                          tuple
                          )

    def __iter__(self) -> Iterator[RatPacBonsaiPair]:
        for f in self._files:
            yield f

    def __len__(self) -> int:
        return len(self._files)

    def __getitem__(self, index) -> RatPacBonsaiPair:
        return self._files[index]

    def _match_bonsai_and_ratpac(self, files: Iterable[str]) -> Iterator[RatPacBonsaiPair]:
        iterpairs = groupby(lambda s: (os.path.basename(os.path.dirname(s)), os.path.basename(s)), files).values()
        sortedpairs = (((l, r) if self._isbonsai(r) else (r, l)) for l, r in iterpairs)
        return itertools.starmap(RatPacBonsaiPair, sortedpairs)

    def _isbonsai(self, filename: str) -> bool:
        return bool(re.match(f".*bonsai_root.*$", filename))
