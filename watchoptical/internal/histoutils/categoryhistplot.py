from typing import Any, Callable, Optional

import boost_histogram as bh
import mplhep
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from watchoptical.internal.histoutils.categoryhistogram import CategoryHistogram


def categoryhistplot(
    hist: CategoryHistogram,
    transformhistogram: Optional[
        Callable[[CategoryHistogram.Item], bh.Histogram]
    ] = None,
    formatlabel: Optional[Callable[[CategoryHistogram.Item], str]] = None,
    ax: Optional[Axes] = None,
    **kwargs: Any,
) -> Axes:
    ax = ax if ax is not None else plt.gca()
    formatlabel = formatlabel if formatlabel is not None else lambda x: x.category
    transformhistogram = (
        transformhistogram if transformhistogram is not None else lambda x: x.histogram
    )
    for item in hist:
        histogram = transformhistogram(item)
        mplhep.histplot(histogram, label=formatlabel(item), **kwargs)
    return ax
