from collections import defaultdict
from copy import deepcopy
from typing import Any, Collection, DefaultDict, Iterator, NamedTuple, Optional, Union

import boost_histogram
import numpy as np


class CategoryMean(Collection):
    Category = Union[Any]
    Moment = Union[boost_histogram.accumulators.WeightedMean]

    class Item(NamedTuple):
        category: "CategoryMean.Category"
        mean: "CategoryMean.Moment"

        @property
        def meanvalue(self) -> float:
            return self.mean.value

        @property
        def meanerror(self) -> float:
            return np.sqrt(self.mean.variance) / np.sqrt(self.mean.sum_of_weights)

    def __init__(self):
        self._points: DefaultDict[
            "CategoryMean.Category", "CategoryMean.Moment"
        ] = defaultdict(boost_histogram.accumulators.WeightedMean)

    def fill(
        self,
        category: "CategoryMean.Category",
        values: Union[float, np.ndarray],
        weight: Optional[Union[float, np.ndarray]] = None,
    ) -> "CategoryMean":
        self._points[category].fill(values, weight=weight)
        return self

    def __iter__(self) -> Iterator[Item]:
        for index, moment in sorted(self._points.items()):
            yield CategoryMean.Item(index, moment)

    def __len__(self) -> int:
        return len(self._points)

    def __contains__(self, __x: object) -> bool:
        return __x in self._points

    def __add__(self, other) -> "CategoryMean":
        result = deepcopy(self)
        for key, value in other._points.items():
            try:
                result._points[key] += value
            except KeyError:
                result._points[key] = deepcopy(value)
        return result
