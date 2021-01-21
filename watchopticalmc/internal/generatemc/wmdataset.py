import itertools
import os
import re
from typing import Dict, Iterable, Iterator, NamedTuple, Optional, Tuple, Union

from toolz import groupby, pipe

from watchopticalmc.internal.utils.filepathutils import findfiles
from watchopticalmc.internal.utils.stringutils import hashfromstrcol


class RatPacBonsaiPair(NamedTuple):
    g4file: str
    bonsaifile: str

    @property
    def eventtype(self) -> str:
        match = re.match(f".*Watchman_(.*){os.sep}.*.root$", self.g4file)
        assert match is not None
        return match.group(1)

    @property
    def rootdirectory(self):
        return os.path.commonpath((self.g4file, self.bonsaifile))


class WatchmanDataset:
    def __init__(
        self,
        filepatterns: Iterable[str],
        name: Optional[str] = None,
        empty_ok: bool = False,
    ):
        self._files: Tuple[RatPacBonsaiPair] = pipe(
            filepatterns, findfiles, self._match_bonsai_and_ratpac, tuple
        )
        if name is None:
            # automatically generate unique name from input files
            name = self._id
        self.name = name
        if len(self) == 0 and not empty_ok:
            raise ValueError("WatchmanDataset is empty", self.name)

    def __iter__(self) -> Iterator[RatPacBonsaiPair]:
        for f in self._files:
            yield f

    def __len__(self) -> int:
        return len(self._files)

    def __getitem__(self, index) -> RatPacBonsaiPair:
        return self._files[index]

    def _match_bonsai_and_ratpac(
        self, files: Iterable[str]
    ) -> Iterator[RatPacBonsaiPair]:
        iterpairs = groupby(
            lambda s: (os.path.basename(os.path.dirname(s)), os.path.basename(s)), files
        ).values()
        iterpairs = self._filterpairs(iterpairs)
        sortedpairs = (
            ((left, right) if self._isbonsai(right) else (right, left))
            for left, right in iterpairs
        )
        return itertools.starmap(RatPacBonsaiPair, sortedpairs)

    def _isbonsai(self, filename: str) -> bool:
        return bool(re.match(".*bonsai_root.*$", filename))

    def _filterpairs(
        self,
        pairs: Iterable[Iterable[str]],
        ignoreerrors: bool = True,
    ) -> Iterable[Tuple[str, str]]:
        failed = []
        for p in pairs:
            result = tuple(p)
            try:
                (left, right) = result
                yield (left, right)
            except ValueError:
                failed.append(result)
        if (not ignoreerrors) and len(failed):
            raise ValueError(
                "Invalid Watchman Dataset. "
                f"{len(failed)} mis-matched files found. "
                "A matching pair is required.",
                failed,
            )

    @property
    def _id(self):
        return hashfromstrcol(s for p in self for s in p)


class WatchmanDataSetCollection:
    def __init__(
        self,
        directories: Dict[str, Union[Iterable[str], str]],
        name: Optional[str] = None,
        empty_ok: bool = False,
    ):
        self.name = name
        self._datasets = {
            k: WatchmanDataset(
                [d] if isinstance(d, str) else d, name=k, empty_ok=empty_ok
            )
            for k, d in directories.items()
        }

    def __iter__(self) -> Iterator[WatchmanDataset]:
        for _, d in sorted(self._datasets.items()):
            yield d

    def __len__(self) -> int:
        return len(self._datasets)

    def __getitem__(self, name: str) -> WatchmanDataset:
        return self._datasets[name]
