from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, List, Optional, Union

import numpy as np
from pandas import DataFrame
from tabulate import tabulate

from watchopticalutils.histoutils.cut import Cut
from watchopticalutils.histoutils.selection import Selection


@dataclass(frozen=True)
class CutStats:
    numtotal: float
    numpassed: float

    @property
    def efficiency(self) -> float:
        return self.numpassed / self.numtotal

    @property
    def numfailed(self) -> float:
        return self.numtotal - self.numpassed

    def __add__(self, other):
        return CutStats(
            self.numtotal + other.numtotal, self.numpassed + other.numpassed
        )


class SelectionStats(Iterable):
    @dataclass(frozen=True)
    class Item:
        cut: Cut
        individual: CutStats
        cumulative: CutStats

        def __add__(self, other: "SelectionStats.Item"):
            if self.cut.name != other.cut.name:
                raise ValueError(f"cannot add {self} and {other}")
            return SelectionStats.Item(
                self.cut,
                self.individual + other.individual,
                self.cumulative + other.cumulative,
            )

    def __init__(self, selection: Selection):
        self._selection = selection
        self._cutcounters = tuple((c, _Counter(), _Counter()) for c in selection.cuts)

    def fill(
        self, data: DataFrame, weight: Optional[Union[float, np.ndarray]] = None
    ) -> "SelectionStats":
        cumulative = None
        for cut, individualcount, cumulativecount in self._cutcounters:
            result = cut(data)
            cumulative = result if cumulative is None else cumulative & result
            individualcount(result, weight)
            cumulativecount(cumulative, weight)
        return self

    def __add__(self, other: "SelectionStats") -> "SelectionStats":
        result = deepcopy(self)
        result._cutcounters = tuple(
            (
                left[0],
                left[1] + right[1],
                left[2] + right[2],
            )
            for left, right in zip(result._cutcounters, other._cutcounters)
        )
        return result

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

    def __add__(self, other: "_Counter") -> "_Counter":
        result = _Counter()
        result.total = self.total + other.total
        result.selected = self.selected + other.selected
        return result


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
