import os
from typing import Any, Callable, Iterable, Optional, Sequence

from matplotlib import pyplot as plt
from tabulate import tabulate

from watchopticalmc.internal.histoutils import CategoryMean, categorymeanplot
from watchopticalmc.internal.opticsanalysis.runopticsanalysis import (
    OpticsAnalysisResult,
)


def plotscatter(data: OpticsAnalysisResult, dest: str = "plots") -> None:
    _plotscatter(data, dest=f"{dest}{os.sep}scatter")


def _plotscatter(data: OpticsAnalysisResult, dest: str) -> None:
    for key, cm in data.scatter.items():
        _simplescatterplot(key, cm, lambda item: item.category.attenuation, dest=dest)
        _simplescattertable(key, cm, dest=dest)
        _relativescattertable(key, cm, dest=dest)


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


def _simplescattertable(
    key: str, data: CategoryMean, ylabel: str = "", dest: str = "plots/scatter"
):
    headers = ["Attenuation", "Event Type", f"{ylabel} Mean", f"{ylabel} Error"]
    table = [
        (
            item.category.attenuation,
            item.category.eventtype,
            item.meanvalue,
            item.meanerror,
        )
        for item in data
    ]
    fname = f"{dest}{os.sep}{key}.txt"
    _dumptable(fname, table, headers=headers)
    return


def _relativescattertable(
    key: str,
    data: CategoryMean,
    ylabel: str = "",
    dest: str = "plots/scatter",
    denominatoritem: Optional[Any] = None,
):
    if denominatoritem is None:
        denominatoritem = min(
            data,
            key=lambda item: (
                "IBD" not in item.category.eventtype,
                abs(item.category.attenuation - 1.0),
            ),
        )
    headers = [
        "Attenuation",
        "Event Type",
        f"{ylabel} Mean",
        f"{ylabel} Error",
        f"Relative {ylabel} Mean",
        f"Relative {ylabel} Error",
    ]
    table = [
        (
            item.category.attenuation,
            item.category.eventtype,
            item.meanvalue,
            item.meanerror,
            _safedivide(item.meanvalue, denominatoritem.meanvalue),
            _safedivide(item.meanerror, denominatoritem.meanvalue),
        )
        for item in data
    ]
    fname = f"{dest}{os.sep}{key}relative.txt"
    _dumptable(fname, table, headers=headers)
    return


def _safedivide(numerator: float, denominator: float):
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return float("nan")


def _dumptable(
    fname: str, table: Iterable[Iterable[Any]], headers: Optional[Sequence[Any]] = None
):
    os.makedirs(os.path.dirname(fname), exist_ok=True)
    with open(fname, "w") as f:
        f.write(tabulate(table, headers=headers if headers else "firstrow"))
