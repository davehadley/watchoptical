from typing import Any, Callable, Optional, Tuple

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from watchopticalutils.histoutils import CategoryMean
from watchopticalutils.histoutils.categoryhistogram import CategoryHistogram


def categorymeanplot(
    data: CategoryMean,
    xtransform: Callable[[CategoryMean.Item], float],
    formatlabel: Optional[Callable[[CategoryHistogram.Item], str]] = None,
    showerr: bool = True,
    ax: Optional[Axes] = None,
    **kwargs: Any,
) -> Axes:
    ax = ax if ax is not None else plt.gca()
    formatlabel = formatlabel if formatlabel is not None else lambda x: x.category
    X, Y, Yerr = _getpoints(data, xtransform)
    if showerr:
        ax.errorbar(X, Y, yerr=Yerr, **kwargs)
    else:
        ax.scatter(X, Y, **kwargs)
    return ax


def _getpoints(
    data: CategoryMean, xtransform: Callable[[CategoryMean.Item], float]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    X = np.array([xtransform(d) for d in data])
    Y = np.array([d.meanvalue for d in data])
    Yerr = np.array([d.meanerror for d in data])
    return (X, Y, Yerr)
