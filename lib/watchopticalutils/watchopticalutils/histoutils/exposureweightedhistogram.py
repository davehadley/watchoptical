from collections import defaultdict
from copy import deepcopy
from typing import Any, Collection, DefaultDict, Iterator, NamedTuple, Optional, Union

import boost_histogram as bh
import numpy as np

from watchopticalutils.histoutils.categoryhistogram import CategoryHistogram


class ExposureWeightedHistogram(Collection):
    class Item(NamedTuple):
        category: CategoryHistogram.Category
        histogram: bh.Histogram
        exposure: float

    def __init__(self, *axes: bh.axis, **kwargs: Any):
        self._hist = CategoryHistogram(*axes, **kwargs)
        self._exposure: DefaultDict[
            CategoryHistogram.Category, bh.accumulators.WeightedSum
        ] = defaultdict(bh.accumulators.WeightedSum)

    def fill(
        self,
        category: CategoryHistogram.Category,
        exposure: float,
        *args: Union[float, np.ndarray],
        weight: Optional[Union[float, np.ndarray]] = None,
    ) -> "ExposureWeightedHistogram":
        self._hist.fill(category, *args, weight=weight)
        self._exposure[category].fill(exposure)
        return self

    def __len__(self) -> int:
        return len(self._hist)

    def __iter__(self) -> Iterator[Item]:
        return self._iterexposureweighted()

    def _iterexposureweighted(self) -> Iterator[Item]:
        for k, v in self._hist:
            yield ExposureWeightedHistogram.Item(
                k, (1.0 / self._exposure[k].value) * v, self._exposure[k]
            )

    def _iterrawhist(self) -> Iterator[Item]:
        for k, v in self._hist:
            yield ExposureWeightedHistogram.Item(k, v, self._exposure[k])

    def __contains__(self, __x: object) -> bool:
        return __x in self._hist

    def __add__(
        self, other: "ExposureWeightedHistogram"
    ) -> "ExposureWeightedHistogram":
        result = deepcopy(self)
        for key, histogram, exposure in other._iterrawhist():
            try:
                result._hist._hist[key] += histogram
                result._exposure[key] += exposure
            except KeyError:
                result._hist._hist[key] = deepcopy(histogram)
                result._exposure[key] = deepcopy(exposure)
        return result
