import itertools
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, MutableMapping, Optional, Sequence

import boost_histogram as bh
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from pandas.core.frame import DataFrame
from tabulate import tabulate
from watchopticalanalysis.algorithm import Algorithm
from watchopticalanalysis.category import Category
from watchopticalanalysis.internal.selectiondefs import SelectionDefs
from watchopticalanalysis.internal.variable import VariableDefs
from watchopticalmc.internal.opticsanalysis.analysiseventtuple import AnalysisEventTuple
from watchopticalutils import timeconstants
from watchopticalutils.collectionutils import summap
from watchopticalutils.histoutils import categoryhistplot, categorymeanplot
from watchopticalutils.histoutils.categorymean import CategoryMean
from watchopticalutils.histoutils.categoryselectionstats import CategorySelectionStats
from watchopticalutils.histoutils.exposureweightedhistogram import (
    ExposureWeightedHistogram,
)
from watchopticalutils.histoutils.selection import Selection


class BasicHist(Algorithm["BasicHist.Result", None]):
    """Makes simple histograms and scatter plots of basic quantities."""

    def __init__(self, output: Path) -> None:
        super().__init__()
        self._output = output

    @dataclass
    class Result:
        hist: MutableMapping[str, ExposureWeightedHistogram] = field(
            default_factory=dict
        )
        scatter: MutableMapping[str, CategoryMean] = field(default_factory=dict)
        selectionstats: MutableMapping[str, CategorySelectionStats] = field(
            default_factory=dict
        )

        def __add__(self, other):
            return BasicHist.Result(
                hist=summap([self.hist, other.hist]),
                scatter=summap(
                    [self.scatter, other.scatter],
                    # lambda lhs, rhs: summap([lhs, rhs], _add_accum),
                ),
                selectionstats=summap([self.selectionstats, other.selectionstats]),
            )

        def __str__(self) -> str:
            return (
                f"BasicHist.Result({len(self.hist)} hist, {len(self.scatter)} scatter)"
            )

    def key(self) -> Optional[str]:
        return "BasicHist"

    def apply(self, data: AnalysisEventTuple) -> "BasicHist.Result":
        result = self.Result()
        _makebasichistograms(data, result.hist)
        _makebasicscatter(data, result.scatter)
        _makebasicattenuationscatter(data, result)
        _makesensitivityscatter(data, result)
        return result

    def finish(self, result: "BasicHist.Result") -> None:
        _plotattenuation(result, dest=str(self._output))
        _plothist(result, dest=str(self._output))
        _plotscatter(result, dest=str(self._output))


def _makebonsaihistogram(
    tree: AnalysisEventTuple,
    binning: bh.axis.Axis,
    x: Callable[[DataFrame], Any],
    w: Optional[Callable[[DataFrame], Any]] = None,
    selection: Selection = SelectionDefs.nominal.value,
    subevent: int = 0,
) -> ExposureWeightedHistogram:
    histo = ExposureWeightedHistogram(binning)
    category = Category.fromAnalysisEventTuple(tree)
    data = selection(tree.bonsai).groupby("mcid").nth(subevent)
    xv = np.asarray(x(data))
    wv = None if not w else np.asarray(w(data))
    histo.fill(category, tree.exposure, xv, weight=wv)
    return histo


def _makebonsaiscatter(
    tree: AnalysisEventTuple,
    x: Callable[[DataFrame], Any],
    w: Optional[Callable[[DataFrame], Any]] = None,
    selection: Selection = SelectionDefs.nominal.value,
    subevent: int = 0,
) -> CategoryMean:
    category = Category.fromAnalysisEventTuple(tree)
    data = selection(tree.bonsai).groupby("mcid").nth(subevent)
    xv = np.asarray(x(data))
    wv = np.ones(shape=xv.shape) if not w else np.asarray(w(data))
    return CategoryMean().fill(category, xv, weight=wv * tree.exposure)


def _makebasichistograms(
    tree: AnalysisEventTuple, hist: MutableMapping[str, ExposureWeightedHistogram]
):
    for (selection, variable, subevent) in itertools.product(
        SelectionDefs, VariableDefs, (None, 0, 1)
    ):
        name = "_".join((variable.name, selection.name, "subevent" + str(subevent)))
        hist[name] = _makebonsaihistogram(
            tree, variable.value.binning, variable.value, selection=selection.value
        )
    return


def _makebasicscatter(
    tree: AnalysisEventTuple, scatter: MutableMapping[str, CategoryMean]
):
    for (selection, variable, subevent) in itertools.product(
        SelectionDefs, VariableDefs, (None, 0, 1)
    ):
        name = "_".join((variable.name, selection.name, "subevent" + str(subevent)))
        scatter[name] = _makebonsaiscatter(
            tree, variable.value, selection=selection.value
        )
    return


def _makebasicattenuationscatter(tree: AnalysisEventTuple, store: BasicHist.Result):
    category = Category.fromAnalysisEventTuple(tree)
    if category.eventtype == "IBD":
        totalq = tree.anal.pmt.pmt_q.groupby("entry").sum().array
        # histogram total Q
        store.hist["ibd_total_charge_by_attenuation"] = ExposureWeightedHistogram(
            bh.axis.Regular(300, 0.0, 150.0)
        ).fill(category, tree.exposure, totalq)
        # calculate mean Q
        meanq = CategoryMean().fill(category, totalq)
        store.scatter["idb_total_charge_by_attenuation_mean"] = meanq
        # calculate mean Q > 10
        meanq_gt10 = CategoryMean().fill(category, totalq[totalq > 10.0])
        store.scatter["idb_total_charge_by_attenuation_mean_gt10"] = meanq_gt10
    return


def _makesensitivityscatter(tree: AnalysisEventTuple, store: BasicHist.Result):
    category = Category.fromAnalysisEventTuple(tree)
    sensitivity = CategoryMean().fill(category, tree.sensitivity.metric)
    store.scatter["sensitvity_metric"] = sensitivity
    return


def _plotattenuation(data: BasicHist.Result, dest="plots"):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for key, label in [
        ("idb_total_charge_by_attenuation_mean", "mean"),
        # ("idb_total_charge_by_attenuation_mean_gt10", "mean | Q > 10"),
    ]:
        points = data.scatter[key]
        processedpoints = [
            (
                category.attenuation / 1.0e3,
                q.value,
                np.sqrt(q.variance) / np.sqrt(q.sum_of_weights),
            )
            for category, q in points
        ]
        X, Y, Yerr = zip(*processedpoints)
        ax.errorbar(list(X), list(Y), yerr=Yerr, ls="", marker="o", label=label)
    ax.legend()
    os.makedirs(dest, exist_ok=True)
    ax.set_ylabel("total charge per event")
    ax.set_xscale("log")
    ax.set_xlabel("attenuation length [m]")
    fig.tight_layout()
    fig.savefig(f"{dest}{os.sep}attenuationmean.png")
    return


def _xlabel(key: str) -> str:
    try:
        return {
            "n9_0": "num PMT hits in 9 ns",
            "n9_1": "num PMT hits in 9 ns",
        }[key]
    except KeyError:
        return key


def _plothist(data: BasicHist.Result, dest):
    for key, h in data.hist.items():
        for yscale in ("linear", "log"):
            fig = Figure()
            ax = fig.add_subplot(111)
            ax = categoryhistplot(
                h,  # type: ignore
                lambda item: item.histogram * timeconstants.SECONDS_IN_WEEK,
                formatlabel=lambda item: f"{item.category.eventtype} "
                f"{item.category.attenuation}",
                ax=ax,
            )
            ax.set_ylabel("events per week")
            ax.set_yscale(yscale)
            ax.set_xlabel(_xlabel(key))
            ax.legend()
            fig.tight_layout()
            fname = f"{dest}{os.sep}{key}_{yscale}.png"
            os.makedirs(os.path.dirname(fname), exist_ok=True)
            fig.savefig(fname)
    return


def _plotscatter(data: BasicHist.Result, dest: str) -> None:
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
