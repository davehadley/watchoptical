import os
from functools import reduce
from operator import add
from typing import Iterable, List

from tabulate import tabulate
from toolz import groupby

from watchopticalutils.histoutils.categoryselectionstats import (
    CategorySelectionStats,
)
from watchopticalmc.internal.opticsanalysis.runopticsanalysis import (
    OpticsAnalysisResult,
)
from watchopticalutils.safedivide import safedivide


def dumpselectiontables(data: OpticsAnalysisResult, dest: str = "plots"):
    for name, stats in data.selectionstats.items():
        _dumpselectiontable(name, _split_stats_by_mc_parameters(stats), dest=dest)


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
