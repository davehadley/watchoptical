from collections import defaultdict
from copy import deepcopy
from functools import reduce
from operator import add
from typing import (
    Any,
    Collection,
    DefaultDict,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Union,
)

import numpy as np
from tabulate import tabulate

from watchoptical.internal.histoutils.selection import Selection
from watchoptical.internal.histoutils.selectionstats import SelectionStats
from watchoptical.internal.utils.safedivide import safedivide


class CategorySelectionStats(Collection):
    Category = Union[Any]

    class Item(NamedTuple):
        category: "CategorySelectionStats.Category"
        selectionstats: SelectionStats

    def __init__(self, selection: Selection):
        self._selection = selection
        self._container: DefaultDict[
            "CategorySelectionStats.Category", SelectionStats
        ] = defaultdict(lambda: SelectionStats(self._selection))

    def fill(
        self,
        category: "CategorySelectionStats.Category",
        data: np.ndarray,
        weight: Optional[Union[float, np.ndarray]] = None,
    ) -> "CategorySelectionStats":
        self._container[category].fill(data, weight=weight)
        return self

    def __iter__(self) -> Iterator[Item]:
        for index, hist in sorted(self._container.items()):
            yield CategorySelectionStats.Item(index, hist)

    def __len__(self) -> int:
        return len(self._container)

    def __contains__(self, __x: object) -> bool:
        return __x in self._container

    def __add__(self, other) -> "CategorySelectionStats":
        result = deepcopy(self)
        for key, value in other._container.items():
            try:
                result._container[key] += value
            except KeyError:
                result._container[key] = deepcopy(value)
        return result

    def __str__(self):
        return str(tabulate(_table(self)))


def _table(catstats: CategorySelectionStats) -> List[List[Any]]:
    total = reduce(add, (item.selectionstats for item in catstats))
    table: List[List[Any]] = [
        [
            "Category" "#",
            "Name",
            "Selected",
            "Efficiency",
            "Purity",
            "Cumulative Selected",
            "Cumulative Efficiency",
            "Cumulative Purity",
        ]
    ]
    for (category, stats) in enumerate(catstats):
        for index, (item, totalitem) in enumerate(zip(stats.selectionstats, total)):
            individualpurity = safedivide(
                item.individual.numpassed, totalitem.individual.numpassed, 0.0
            )
            cumulativepurity = safedivide(
                item.individual.numpassed, totalitem.cumulative.numpassed, 0.0
            )
            table.append(
                [
                    str(category),
                    str(index),
                    item.cut.name if item.cut.name else f"Cut {index}",
                    item.individual.numpassed,
                    item.individual.efficiency,
                    individualpurity,
                    item.cumulative.numpassed,
                    item.cumulative.efficiency,
                    cumulativepurity,
                ]
            )
    return table
