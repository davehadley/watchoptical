import math
import os
from functools import reduce
from operator import add
from pathlib import Path
from typing import Dict, Generator, Iterable, List, NamedTuple, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate
from toolz import groupby
from watchopticalanalysis.algorithm import Algorithm
from watchopticalanalysis.category import Category
from watchopticalanalysis.internal.selectiondefs import SelectionDefs
from watchopticalmc.internal.opticsanalysis.analysiseventtuple import AnalysisEventTuple
from watchopticalutils.collectionutils import summap
from watchopticalutils.histoutils.categoryselectionstats import (
    CategorySelectionStats,
    SelectionStats,
)
from watchopticalutils.safedivide import safedivide


class SelectionTables(Algorithm["SelectionTables.Result", None]):
    """Makes cutflow tables of each selection."""

    def __init__(self, output: Path) -> None:
        self._output = output
        super().__init__()

    class Result:
        def __init__(self, stats: Dict[SelectionDefs, CategorySelectionStats]) -> None:
            self.stats = stats

        def __add__(self, rhs: "SelectionTables.Result") -> "SelectionTables.Result":
            return SelectionTables.Result(summap((self.stats, rhs.stats)))

    def key(self) -> Optional[str]:
        return "SelectionTables"

    def apply(self, data: AnalysisEventTuple) -> "SelectionTables.Result":
        stats = _make_stats(data)
        return self.Result(stats=stats)

    def finish(self, result: "SelectionTables.Result") -> None:
        path = self._output / "selectiontables"
        _dumpselectiontables(result, dest=path)
        _summaryplot(result, dest=path)
        return


def _make_stats(
    tree: AnalysisEventTuple,
) -> Dict[SelectionDefs, CategorySelectionStats]:
    category = Category.fromAnalysisEventTuple(tree)
    return {
        selection: CategorySelectionStats(selection.value).fill(
            category, tree.bonsai, tree.exposure
        )
        for selection in list(SelectionDefs)
    }


def _dumpselectiontables(data: SelectionTables.Result, dest: Path = Path("plots")):
    for name, stats in data.stats.items():
        _dumpselectiontable(name.name, _split_stats_by_mc_parameters(stats), dest=dest)


def _dumpselectiontable(
    name: str,
    stats: List[List[CategorySelectionStats.Item]],
    dest: Path = Path("plots"),
):
    fname = f"{dest}{os.sep}tab{os.sep}selection_{name}.txt"
    os.makedirs(os.path.dirname(fname), exist_ok=True)
    with open(fname, "w") as f:
        for s in stats:
            f.write(_selectiontabletostring(name, s))


def _selectiontabletostring(
    name: str, stats: Iterable[CategorySelectionStats.Item]
) -> str:
    return tabulate(_table(stats))


def _split_stats_by_mc_parameters(
    stats: CategorySelectionStats,
) -> List[List[CategorySelectionStats.Item]]:
    # it doesn't make sense to put categories with different MC parameters together
    # into the same table as we would calculate the wrong purities
    def keyfunc(item: CategorySelectionStats.Item):
        return ("%.6e" % item.category.attenuation, "%.6e" % item.category.scattering)

    return [list(group) for group in groupby(keyfunc, stats).values()]


def _table(catstats: Iterable[CategorySelectionStats.Item]) -> List[List[str]]:
    total = reduce(add, (item.selectionstats for item in catstats))
    table: List[List[str]] = [
        [
            "Cat #",
            "Category",
            "Cut #",
            "Name",
            "Selected",
            "Efficiency",
            "Purity",
            "Cumulative Selected",
            "Cumulative Efficiency",
            "Cumulative Purity",
        ]
    ]
    for categoryindex, (category, stats) in enumerate(catstats):
        for index, (item, totalitem) in enumerate(zip(stats, total)):
            individualpurity = safedivide(
                item.individual.numpassed, totalitem.individual.numpassed, 0.0
            )
            cumulativepurity = safedivide(
                item.cumulative.numpassed, totalitem.cumulative.numpassed, 0.0
            )
            table.append(
                [
                    f"{categoryindex}",
                    f"{category}",
                    str(index),
                    item.cut.name if item.cut.name else f"Cut {index}",
                    "%.3e" % item.individual.numpassed,
                    "%.3f" % item.individual.efficiency,
                    "%.3f" % individualpurity,
                    "%.3e" % item.cumulative.numpassed,
                    "%.3f" % item.cumulative.efficiency,
                    "%.3f" % cumulativepurity,
                ]
            )
    return table


def _summaryplot(result: SelectionTables.Result, dest: Path) -> None:
    dest = dest / "summary"
    for k, v in result.stats.items():
        _make_efficiency_plot(k, v, dest)
    return


def _make_efficiency_plot(
    selection: SelectionDefs, stats: CategorySelectionStats, dest: Path
):
    for xattr, groupbyattr in [
        ("attenuation", "scattering"),
        ("scattering", "attenuation"),
    ]:
        subplotdata = list(_iter_subplots(stats, xattr=xattr, groupbyattr=groupbyattr))
        assert len(subplotdata) > 0
        subplotcombos = [("all", "all", subplotdata)] + [
            ("single", f"{p.groupname}_{p.groupvalue}", [p]) for p in subplotdata
        ]
        for prefix, label, subplotdata in subplotcombos:
            _make_efficiency_summary_plot(
                subplotdata,
                dest / prefix / f"{selection.value.name}_resolution_by_{xattr}_{label}",
            )
    return


class _SubplotData(NamedTuple):
    groupname: str
    groupvalue: float
    xvarname: str
    x: np.ndarray
    signaleff: np.ndarray
    signalefferr: np.ndarray
    signalpurity: np.ndarray
    signalpurityerr: np.ndarray


def _iter_subplots(
    selectionstats: CategorySelectionStats,
    xattr: str = "attenuation",
    groupbyattr: str = "scattering",
) -> Generator[_SubplotData, None, None]:
    signalonly = filter(
        lambda item: "ibd" in item.category.eventtype.lower(), selectionstats
    )
    groupedbyattr = groupby(
        lambda item: getattr(item.category, groupbyattr), signalonly
    )
    for attrvalue, items in groupedbyattr.items():
        X = [getattr(it.category, xattr) for it in items]
        eff, efferr = zip(*[_calcefficiency(it.selectionstats) for it in items])
        purity, purityerr = zip(
            *[
                _calcpurity(it.selectionstats, _calctotal(it.category, selectionstats))
                for it in items
            ]
        )
        (X, eff, efferr, purity, purityerr) = (
            np.array(it) for it in (X, eff, efferr, purity, purityerr)
        )
        yield _SubplotData(
            groupbyattr, attrvalue, xattr, X, eff, efferr, purity, purityerr
        )


def _calcefficiency(stats: SelectionStats) -> Tuple[np.ndarray, np.ndarray]:
    item = stats[-1]
    return (item.cumulative.efficiency, item.cumulative.binomial_efficiency_error)


def _calcpurity(
    stats: SelectionStats, totalstats: SelectionStats
) -> Tuple[np.ndarray, np.ndarray]:
    item = stats[-1]
    totalitem = totalstats[-1]
    purity = safedivide(item.cumulative.numpassed, totalitem.cumulative.numpassed, 0.0)
    error = _binomial_error(purity, totalitem.cumulative.numpassedeffective)
    return (purity, error)


def _calctotal(
    category: Category, selectionstats: CategorySelectionStats
) -> SelectionStats:
    return reduce(
        add,
        (
            item.selectionstats
            for item in selectionstats
            if item.category.attenuation == category.attenuation
            and item.category.scattering == category.scattering
        ),
    )


def _binomial_error(efficiency: float, denominator: float) -> float:
    return math.sqrt(efficiency * (1 - efficiency) / denominator)


def _make_efficiency_summary_plot(
    data: Iterable[_SubplotData], dest: Path, ext: str = ".svg"
):
    data = list(data)
    assert len(data) > 0
    plotcombos = [
        (
            dest.with_name(dest.name + "_eff" + ext),
            "signaleff",
            "signalefferr",
            r"signal efficiency",
        ),
        (
            dest.with_name(dest.name + "_purity" + ext),
            "signalpurity",
            "signalpurityerr",
            r"signal purity",
        ),
    ]
    for fname, yval, yerr, ylabel in plotcombos:
        fig = plt.figure()
        fig.tight_layout()
        ax = fig.add_subplot(111)
        for d in data:
            xvalues = d.x
            yvalues = getattr(d, yval)
            yerrs = getattr(d, yerr)
            label = f"{d.groupname}={d.groupvalue}"
            ax.errorbar(xvalues, yvalues, yerr=yerrs, label=label)
            ax.set_xlabel(d.xvarname)
            ax.set_ylabel(ylabel)
        ax.legend()
        fname.parent.mkdir(exist_ok=True, parents=True)
        fig.savefig(fname)
        plt.close(fig)
