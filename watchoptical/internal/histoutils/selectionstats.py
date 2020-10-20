from typing import Any, Iterable, Iterator, List, NamedTuple, Optional, Union

import numpy as np
from pandas import DataFrame
from tabulate import tabulate

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


class SelectionStats(Iterable):
    class Item(NamedTuple):
        cut: Cut
        individual: CutStats
        cumulative: CutStats

    def __init__(self, selection: Selection):
        self._selection = selection
        self._cutcounters = tuple((c, _Counter(), _Counter()) for c in selection.cuts)

    def fill(self, data: DataFrame, weight: Optional[Union[float, np.ndarray]] = None):
        cumulative = None
        for cut, individualcount, cumulativecount in self._cutcounters:
            result = cut(data)
            cumulative = result if cumulative is None else cumulative & result
            individualcount(result, weight)
            cumulativecount(cumulative, weight)

    def __len__(self) -> int:
        return len(self._cutcounters)

    def __iter__(self) -> Iterator[Item]:
        for index in range(len(self)):
            yield self[index]

    def __contains__(self, __x: object) -> bool:
        pass

    def __getitem__(self, index: int) -> Item:
        cut, individualcount, cumulativecount = self._cutcounters[index]
        return self.Item(
            cut, individualcount.tocutstats(), cumulativecount.tocutstats()
        )

    def _totable(self):
        pass

    def __str__(self):
        return str(tabulate(_table(self)))


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


def _table(stats: SelectionStats) -> List[List[Any]]:
    table = [
        [
            "#",
            "Name",
            "Selected",
            "Efficiency",
            "Cumulative Selected",
            "Cumulative Efficiency",
        ]
    ]
    for index, item in enumerate(stats):
        table.append(
            [
                str(index),
                item.cut.name if item.cut.name else f"Cut {index}",
                item.individual.numpassed,
                item.individual.efficiency,
                item.cumulative.numpassed,
                item.cumulative.efficiency,
            ]
        )
    return table
