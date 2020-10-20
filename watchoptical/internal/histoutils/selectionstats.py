from typing import Collection, Iterator, NamedTuple, Optional, Union

import numpy as np
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
    def numfailed(self) -> float:
        return self.numtotal - self.numpassed


class SelectionStats(Collection):
    class Item(NamedTuple):
        cut: Cut
        individual: CutStats
        cumulative: CutStats

    def __init__(self, selection: Selection):
        self._cutcounters = tuple((c, _Counter(), _Counter()) for c in selection.cuts)

    def fill(self, data: DataFrame, weight: Optional[Union[float, np.ndarray]] = None):
        cumulative = None
        for cut, individualcount, cumulativecount in self._cutcounters:
            result = cut(data)
            cumulative = result if cumulative is None else cumulative & result
            individualcount(result, weight)
            cumulativecount(cumulative, weight)

    # def _computeweight(self, weight: Union[np.ndarray, float],
    #                    data: np.ndarray) -> np.ndarray:
    #     if isinstance(weight, float):
    #         return np.broadcast_to(weight, data)
    #     else:
    #         return weight[data]

    def __len__(self) -> int:
        return len(self._cutcounters)

    def __iter__(self) -> Iterator[Item]:
        pass

    def __contains__(self, __x: object) -> bool:
        pass

    def __getitem__(self, index: int) -> Item:
        cut, individualcount, cumulativecount = self._cutcounters[index]
        return self.Item(
            cut, individualcount.tocutstats(), cumulativecount.tocutstats()
        )


class _Counter:
    def __init__(self):
        self.total = 0.0
        self.selected = 0.0

    def __call__(
        self, isselected: np.ndarray, weight: Optional[Union[float, np.ndarray]] = None
    ):
        if weight is None:
            weight = 1.0
        self.total += np.sum(np.broadcast_to(weight, isselected.shape))
        self.selected += np.sum(isselected * weight)

    def tocutstats(self):
        return CutStats(numtotal=self.total, numpassed=self.selected)
