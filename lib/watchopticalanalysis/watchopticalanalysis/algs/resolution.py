import itertools
from pathlib import Path
from typing import Any, Callable, Dict, NamedTuple, Optional

import bootstraphistogram
import numpy as np
from pandas.core.frame import DataFrame
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
