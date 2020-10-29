import os

from watchoptical.internal.histoutils.categoryselectionstats import (
    CategorySelectionStats,
)
from watchoptical.internal.opticsanalysis.runopticsanalysis import OpticsAnalysisResult


def dumpselectiontables(data: OpticsAnalysisResult, dest: str = "plots"):
    for name, stats in data.selectionstats.items():
        _dumpselectiontable(name, stats, dest=dest)


def _dumpselectiontable(name: str, stats: CategorySelectionStats, dest: str = "plots"):
    fname = f"{dest}{os.sep}tab{os.sep}selection_{name}.txt"
    os.makedirs(os.path.dirname(fname), exist_ok=True)
    with open(fname, "w") as f:
        f.write(_selectiontabletostring(name, stats))


def _selectiontabletostring(name: str, stats: CategorySelectionStats) -> str:
    return "\n".join(
        f"Category:{item.category}\n" f"Cuts:\n{item.selectionstats}\n"
        for item in stats
    )
