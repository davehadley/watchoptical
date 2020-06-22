from collections import defaultdict
from copy import deepcopy
from typing import NamedTuple, Iterator, Collection, Union, Optional, Any, Callable

import boost_histogram as bh
import numpy as np
import mplhep
from matplotlib.axes import Axes


class CategoryHistogram(Collection):
    class Item(NamedTuple):
        category: str
        histogram: bh.Histogram

    def __init__(self, *axes: bh.axis.Axis, **kwargs: Any):
        self._args = axes
        self._kwargs = kwargs
        self._hist = dict()

    def fill(self, category: str, *args: np.ndarray, weight: Optional[np.ndarray] = None):
        if category not in self._hist:
            self._hist[category] = bh.Histogram(*self._args, **self._kwargs)
        self._hist[category].fill(*args, weight=weight)

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



def categoryhistplot(hist: CategoryHistogram,
                     transformhistogram: Optional[Callable[[CategoryHistogram.Item], bh.Histogram]] = None,
                     formatlabel: Optional[Callable[[CategoryHistogram.Item], str]] = None,
                     **kwargs: Any) -> Optional[Axes]:
    ax = None
    formatlabel = formatlabel if formatlabel is not None else lambda x: x.category
    transformhistogram = transformhistogram if transformhistogram is not None else lambda x: x.histogram
    for item in hist:
        histogram = transformhistogram(item)
        ax = mplhep.histplot(histogram, label=formatlabel(item), **kwargs)
    return ax


class ExposureWeightedHistogram(Collection):

    class Item(NamedTuple):
        category: str
        histogram :bh.Histogram
        exposure: float

    def __init__(self, *axes: bh.axis, **kwargs: Any):
        self._hist = CategoryHistogram(*axes, **kwargs)
        self._exposure = defaultdict(bh.accumulators.WeightedSum)

    def fill(self, category: str, exposure: float, *args: np.ndarray, weight: Optional[np.ndarray] = None):
        self._hist.fill(category, *args, weight=weight)
        self._exposure[category].fill(exposure)
        return

    def __len__(self) -> int:
        return len(self._hist)

    def __iter__(self) -> Iterator[Item]:
        for k, v in self._hist:
            yield ExposureWeightedHistogram.Item(k, (1.0 / self._exposure[k].value) * v, self._exposure[k])

    def __contains__(self, __x: object) -> bool:
        return __x in self._hist

    def __add__(self, other: "ExposureWeightedHistogram") -> "ExposureWeightedHistogram":
        result = deepcopy(self)
        for key, histogram, exposure in other:
            try:
                result._hist._hist[key] += histogram
                result._exposure[key] += exposure
            except KeyError:
                result._hist._hist[key] = deepcopy(histogram)
                result._exposure[key] = deepcopy(exposure)
        return result
