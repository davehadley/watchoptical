import os
from typing import Callable

from matplotlib import pyplot as plt

from watchoptical.internal.histoutils import CategoryMean, categorymeanplot
from watchoptical.internal.opticsanalysis.runopticsanalysis import OpticsAnalysisResult


def plotscatter(data: OpticsAnalysisResult, dest: str = "plots") -> None:
    _plotscatter(data, dest=f"{dest}{os.sep}scatter")


def _plotscatter(data: OpticsAnalysisResult, dest: str) -> None:
    for key, cm in data.scatter.items():
        _simplescatterplot(key, cm, lambda item: item.category.attenuation, dest=dest)


def _simplescatterplot(
    key: str,
    data: CategoryMean,
    xtransform: Callable[[CategoryMean.Item], float],
    xlabel: str = "",
    ylabel: str = "",
    dest: str = "plots/scatter",
):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax = categorymeanplot(
        data,  # type: ignore
        xtransform=xtransform,
        formatlabel=lambda item: f"{item.category.eventtype} "
        f"{item.category.attenuation}",
        ax=ax,
    )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    fig.tight_layout()
    fname = f"{dest}{os.sep}{key}.png"
    os.makedirs(os.path.dirname(fname), exist_ok=True)
    fig.savefig(fname)
