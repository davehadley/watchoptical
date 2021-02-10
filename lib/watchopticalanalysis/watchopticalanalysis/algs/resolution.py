import itertools
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Tuple,
)

import bootstraphistogram
import matplotlib.pyplot as plt
import numpy as np
from bootstraphistogram.bootstraphistogram import BootstrapHistogram
from pandas.core.frame import DataFrame
from tabulate import tabulate
from toolz.itertoolz import groupby
from watchopticalanalysis.algorithm import Algorithm
from watchopticalanalysis.category import Category
from watchopticalanalysis.internal.selectiondefs import SelectionDefs
from watchopticalanalysis.internal.variable import (
    AnalysisVariableDefs,
    BonsaiVariableDefs,
)
from watchopticalmc import AnalysisEventTuple
from watchopticalutils.collectionutils import summap
from watchopticalutils.histoutils.categorybootstraphistogram import (
    CategoryBootstrapHistogram,
)
from watchopticalutils.histoutils.selection import Selection

_BONSAIVARIABLES = [
    BonsaiVariableDefs.innerPE_over_mcenergy,
    BonsaiVariableDefs.deltar,
]

_ANALYSISVARIABLES = [
    AnalysisVariableDefs.totalcharge,
    AnalysisVariableDefs.totalcharge_over_mcenergy,
]


class _Key(NamedTuple):
    variable: str
    selection: str
    subevent: Optional[int]


class Resolution(Algorithm["Resolution.Result", None]):
    """Plot resolution."""

    def __init__(self, output: Path) -> None:
        self._output = output
        super().__init__()

    class Result:
        def __init__(self, hist: Dict[_Key, CategoryBootstrapHistogram]) -> None:
            self.hist = hist

        def __add__(self, rhs: "Resolution.Result") -> "Resolution.Result":
            return Resolution.Result(summap((self.hist, rhs.hist)))

    def key(self) -> Optional[str]:
        return "Resolution"

    def apply(self, data: AnalysisEventTuple) -> "Resolution.Result":
        return self.Result(_make_resolution(data))

    def finish(self, result: "Resolution.Result") -> None:
        _dumpresolutiontables(result, dest=self._output)
        _summaryplot(result, dest=self._output)
        return


def _make_resolution(
    tree: AnalysisEventTuple,
) -> Dict[_Key, CategoryBootstrapHistogram]:
    hist: Dict[_Key, CategoryBootstrapHistogram] = {}
    _make_bonsai_hists(tree, hist)
    _make_analysisvar_hists(tree, hist)
    return hist


def _make_bonsai_hists(
    tree: AnalysisEventTuple, hist: Dict[_Key, CategoryBootstrapHistogram]
):
    for (selection, variable, subevent) in itertools.product(
        SelectionDefs, _BONSAIVARIABLES, (None, 0, 1)
    ):
        key = _Key(variable.name, selection.name, subevent)
        hist[key] = _makebonsaibootstraphistogram(
            tree, variable.value.binning, variable.value, selection=selection.value
        )
    return


def _make_analysisvar_hists(
    tree: AnalysisEventTuple, hist: Dict[_Key, CategoryBootstrapHistogram]
):
    for (selection, variable, subevent) in itertools.product(
        SelectionDefs, _ANALYSISVARIABLES, (None, 0, 1)
    ):
        key = _Key(variable.name, selection.name, subevent)
        hist[key] = _makeanalysisvarbootstraphistogram(
            tree, variable.value.binning, variable.value, selection=selection.value
        )
    return hist


def _makebonsaibootstraphistogram(
    tree: AnalysisEventTuple,
    binning: bootstraphistogram.axis.Axis,
    x: Callable[[DataFrame], Any],
    w: Optional[Callable[[DataFrame], Any]] = None,
    selection: Selection = SelectionDefs.nominal.value,
    subevent: int = 0,
) -> CategoryBootstrapHistogram:
    histo = CategoryBootstrapHistogram(binning)
    category = Category.fromAnalysisEventTuple(tree)
    data = selection(tree.bonsai).groupby("mcid").nth(subevent)
    xv = np.asarray(x(data))
    wv = None if not w else np.asarray(w(data))
    histo.fill(category, xv, weight=wv)
    return histo


def _makeanalysisvarbootstraphistogram(
    tree: AnalysisEventTuple,
    binning: bootstraphistogram.axis.Axis,
    x: Callable[[AnalysisEventTuple], Any],
    w: Optional[Callable[[AnalysisEventTuple], Any]] = None,
    selection: Selection = SelectionDefs.nominal.value,
    subevent: int = 0,
) -> CategoryBootstrapHistogram:
    histo = CategoryBootstrapHistogram(binning)
    category = Category.fromAnalysisEventTuple(tree)
    xv = np.asarray(x(tree))
    wv = None if not w else np.asarray(w(tree))
    histo.fill(category, xv, weight=wv)
    return histo


def _dumpresolutiontables(result: Resolution.Result, dest: Path) -> None:
    dest = dest / "resolution"
    for k, v in result.hist.items():
        _make_resolution_table(k, v, dest)
    return


def _make_resolution_table(key: _Key, hist: CategoryBootstrapHistogram, dest: Path):
    table = _make_resolution_table_str(hist)
    for (tablefmt, ext) in [
        ("simple", ".md"),
        ("csv", "csv"),
        ("html", "html"),
        ("plain", "txt"),
    ]:
        path = dest / tablefmt / ("_".join(map(str, key)) + "." + ext)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(tabulate(table, tablefmt=tablefmt))


def _make_resolution_table_str(hist: CategoryBootstrapHistogram) -> List[List[Any]]:
    table = [
        [
            "Event type",
            "Attenuation",
            "Scattering",
            "mean",
            "mear err.",
            "std. dev.",
            "std. dev. err.",
        ]
    ]
    table += _make_resolution_table_rows(hist)
    return table


def _make_resolution_table_rows(hist: CategoryBootstrapHistogram) -> List[List[Any]]:
    return [_calcrow(item.category, item.histogram) for item in sorted(hist)]


def _calcrow(category: Category, histogram: BootstrapHistogram) -> List[Any]:
    mean, meanerr = _calcmu(histogram)
    sigma, sigmaerr = _calcsigma(histogram)
    return [*category, mean, meanerr, sigma, sigmaerr]


def _calcmu(histogram: BootstrapHistogram) -> Tuple[float, float]:
    def binnedavg(h):
        try:
            return np.average(h.axes[0].centers, weights=h.view())
        except ZeroDivisionError:
            return np.NaN

    mu = binnedavg(histogram.nominal)
    err = np.std(
        [
            binnedavg(histogram.samples[:, sample])
            for sample in range(histogram.numsamples)
        ]
    )
    return (mu, err)


def _calcsigma(histogram: BootstrapHistogram) -> Tuple[float, float]:
    def binnedstd(h):
        try:
            values = h.axes[0].centers
            weights = h.view()
            mu = np.average(values, weights=weights)
            var = np.average((values - mu) ** 2, weights=weights)
            return np.sqrt(var)
        except ZeroDivisionError:
            return np.NaN

    std = binnedstd(histogram.nominal)
    err = np.std(
        [
            binnedstd(histogram.samples[:, sample])
            for sample in range(histogram.numsamples)
        ]
    )
    return (std, err)


def _summaryplot(result: Resolution.Result, dest: Path) -> None:
    dest = dest / "resolution"
    for k, v in result.hist.items():
        if k.subevent is not None and k.subevent == 0:
            _make_resolution_plot(k, v, dest)
    return


def _make_resolution_plot(key: _Key, hist: CategoryBootstrapHistogram, dest: Path):
    for xattr, groupbyattr in [
        ("attenuation", "scattering"),
        ("scattering", "attenuation"),
    ]:
        subplotdata = list(_iter_subplots(hist, xattr=xattr, groupbyattr=groupbyattr))
        assert len(subplotdata) > 0
        subplotcombos = [("all", "all", subplotdata)] + [
            ("single", f"{p.groupname}_{p.groupvalue}", [p]) for p in subplotdata
        ]
        for prefix, label, subplotdata in subplotcombos:
            _make_resolution_summary_plot(
                subplotdata,
                dest
                / "summary"
                / prefix
                / f"{key.variable}_{key.selection}_resolution_by_{xattr}_{label}",
            )
    return


class _SubplotData(NamedTuple):
    groupname: str
    groupvalue: float
    xvarname: str
    x: np.ndarray
    mean: np.ndarray
    meanerr: np.ndarray
    sigma: np.ndarray
    sigmaerr: np.ndarray


def _iter_subplots(
    hist: CategoryBootstrapHistogram,
    xattr: str = "attenuation",
    groupbyattr: str = "scattering",
) -> Generator[_SubplotData, None, None]:
    signalonly = filter(lambda item: "ibd" in item.category.eventtype.lower(), hist)
    groupedbyattr = groupby(
        lambda item: getattr(item.category, groupbyattr), signalonly
    )
    for attrvalue, items in groupedbyattr.items():
        X = [getattr(it.category, xattr) for it in items]
        mean, meanerr = zip(*[_calcmu(it.histogram) for it in items])
        sigma, sigmaerr = zip(*[_calcsigma(it.histogram) for it in items])
        (X, mean, meanerr, sigma, sigmaerr) = (
            np.array(it) for it in (X, mean, meanerr, sigma, sigmaerr)
        )
        yield _SubplotData(
            groupbyattr, attrvalue, xattr, X, mean, meanerr, sigma, sigmaerr
        )


def _make_resolution_summary_plot(
    data: Iterable[_SubplotData], dest: Path, ext: str = ".svg"
):
    data = list(data)
    assert len(data) > 0
    plotcombos = [
        (dest.with_name(dest.name + "_mean" + ext), "mean", "meanerr", r"$\mu$"),
        (dest.with_name(dest.name + "_stddev" + ext), "sigma", "sigmaerr", r"$\sigma$"),
    ]
    for fname, yval, yerr, ylabel in plotcombos:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for d in data:
            xvalues = d.x
            yvalues = getattr(d, yval)
            yerrs = getattr(d, yerr)
            label = f"{d.groupname}={d.groupvalue}"
            ax.errorbar(
                xvalues,
                yvalues,
                yerr=yerrs,
                label=label,
                marker="o",
                capsize=10.0,
                alpha=0.9,
            )
            ax.set_xlabel(d.xvarname)
            ax.set_ylabel(ylabel)
        ax.legend(fontsize="small")
        fname.parent.mkdir(exist_ok=True, parents=True)
        fig.tight_layout()
        fig.savefig(fname)
        plt.close(fig)
