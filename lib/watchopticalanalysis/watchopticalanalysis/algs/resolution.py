import itertools
from pathlib import Path
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple

import bootstraphistogram
import numpy as np
from bootstraphistogram.bootstraphistogram import BootstrapHistogram
from pandas.core.frame import DataFrame
from tabulate import tabulate
from watchopticalanalysis.algorithm import Algorithm
from watchopticalanalysis.category import Category
from watchopticalanalysis.internal.selectiondefs import SelectionDefs
from watchopticalanalysis.internal.variable import VariableDefs
from watchopticalmc import AnalysisEventTuple
from watchopticalutils.collectionutils import summap
from watchopticalutils.histoutils.categorybootstraphistogram import (
    CategoryBootstrapHistogram,
)
from watchopticalutils.histoutils.selection import Selection

_VARIABLES = [
    VariableDefs.innerPE_over_mcenergy,
    VariableDefs.deltar,
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
        return


def _make_resolution(
    tree: AnalysisEventTuple,
) -> Dict[_Key, CategoryBootstrapHistogram]:
    hist = {}
    for (selection, variable, subevent) in itertools.product(
        SelectionDefs, VariableDefs, (None, 0, 1)
    ):
        key = _Key(variable.name, selection.name, subevent)
        hist[key] = _makebonsaibootstraphistogram(
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


def _dumpresolutiontables(result: Resolution.Result, dest: Path) -> None:
    dest = dest / "resolution"
    for k, v in result.hist.items():
        _make_resolution_table(k, v, dest)
    return


def _make_resolution_table(key: _Key, hist: CategoryBootstrapHistogram, dest: Path):
    table = _make_resolution_table_str(hist)
    path = dest / "_".join(map(str, key))
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(table)


def _make_resolution_table_str(hist: CategoryBootstrapHistogram) -> str:
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
    return tabulate(table)


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
    return _calcmu(histogram)
