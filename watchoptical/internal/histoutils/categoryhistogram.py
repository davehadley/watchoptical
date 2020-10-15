from copy import deepcopy
from typing import Any, Collection, Dict, Iterator, NamedTuple, Optional, Union

import boost_histogram as bh
import numpy as np


class CategoryHistogram(Collection):
    Category = Union[Any]

    class Item(NamedTuple):
        category: "CategoryHistogram.Category"
        histogram: bh.Histogram

    def __init__(self, *axes: bh.axis.Axis, **kwargs: Any):
        self._args = axes
        self._kwargs = kwargs
        self._hist: Dict["CategoryHistogram.Category", bh.Histogram] = dict()

    def fill(
        self,
        category: "CategoryHistogram.Category",
        *args: Union[float, np.ndarray],
        weight: Optional[Union[float, np.ndarray]] = None,
    ) -> "CategoryHistogram":
        if category not in self._hist:
            self._hist[category] = bh.Histogram(*self._args, **self._kwargs)
        self._hist[category].fill(*args, weight=weight)
        return self

    def __iter__(self) -> Iterator[Item]:
        for index, hist in sorted(self._hist.items()):
            yield CategoryHistogram.Item(index, hist)

    def __len__(self) -> int:
        return len(self._hist)

    def __contains__(self, __x: object) -> bool:
        return __x in self._hist

    def __add__(self, other) -> "CategoryHistogram":
        result = deepcopy(self)
        for key, value in other._hist.items():
            try:
                result._hist[key] += value
            except KeyError:
                result._hist[key] = deepcopy(value)
        return result
