from collections import defaultdict
from copy import deepcopy
from typing import Any, Collection, DefaultDict, Iterator, NamedTuple, Optional, Union

import numpy as np

from watchoptical.internal.histoutils.selection import Selection
from watchoptical.internal.histoutils.selectionstats import SelectionStats


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
