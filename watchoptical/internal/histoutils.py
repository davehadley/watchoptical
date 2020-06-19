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
        axes = list(axes) + [bh.axis.StrCategory([], growth=True)]
        self._hist = bh.Histogram(*axes, **kwargs)

    def fill(self, category: str, *args: np.ndarray, weight: Optional[np.ndarray] = None):
        self._hist.fill(*args, category, weight=weight)

    def __iter__(self):
        for index in sorted(self._categoryaxis):
            yield CategoryHistogram.Item(index, self._hist[..., bh.loc(index)])

    def __len__(self) -> int:
        return len(self._categoryaxis)

    def __contains__(self, __x: object) -> bool:
        return __x in set(self._categoryaxis)

    def __add__(self, other) -> "CategoryHistogram":
        result = deepcopy(self)
        result._hist += other._hist
        return result

    @property
    def _categoryaxis(self):
        return self._hist.axes[-1]


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
