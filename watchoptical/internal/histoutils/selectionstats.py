from typing import Collection, Iterator, NamedTuple, Union

from pandas import DataFrame

from watchoptical.internal.histoutils.cut import Cut
from watchoptical.internal.histoutils.selection import Selection


class CutStats(NamedTuple):
    numtotal: float
    numpassed: float

    @property
    def efficiency(self) -> float:
        return self.numpassed / self.numtotal

    @property
    def nfailed(self) -> float:
        return self.numtotal - self.numpassed


class SelectionStats(Collection):
    class Item(NamedTuple):
        cut: Cut
        individual: CutStats
        cumulative: CutStats

    def __init__(self, selection: Selection):
        self._selection = selection

    def fill(self, data: DataFrame):
        pass

    def __len__(self) -> int:
        return len(self._selection.cuts)

    def __iter__(self) -> Iterator[Item]:
        pass

    def __contains__(self, __x: object) -> bool:
        pass

    def __getitem__(self, item: Union[int, str, Cut]) -> Item:
        pass
