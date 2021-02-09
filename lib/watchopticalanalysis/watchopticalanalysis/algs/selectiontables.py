import os
from functools import reduce
from operator import add
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from tabulate import tabulate
from toolz import groupby
from watchopticalanalysis.algorithm import Algorithm
from watchopticalanalysis.category import Category
from watchopticalanalysis.internal.selectiondefs import SelectionDefs
from watchopticalmc.internal.opticsanalysis.analysiseventtuple import AnalysisEventTuple
from watchopticalutils.collectionutils import summap
from watchopticalutils.histoutils.categoryselectionstats import CategorySelectionStats
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
        _dumpselectiontables(result, dest=str(self._output))
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


def _dumpselectiontables(data: SelectionTables.Result, dest: str = "plots"):
    for name, stats in data.stats.items():
        _dumpselectiontable(name.name, _split_stats_by_mc_parameters(stats), dest=dest)


def _dumpselectiontable(
    name: str,
    stats: List[List[CategorySelectionStats.Item]],
    dest: str = "plots",
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
