from typing import Dict, Optional

from watchopticalanalysis.algorithm import Algorithm
from watchopticalanalysis.category import Category
from watchopticalanalysis.internal.selectiondefs import SelectionDefs
from watchopticalmc.internal.opticsanalysis.analysiseventtuple import AnalysisEventTuple
from watchopticalutils.collectionutils import summap
from watchopticalutils.histoutils.categoryselectionstats import CategorySelectionStats


class SelectionTables(Algorithm["SelectionTables.Result", None]):
    """Test algorithm does nothing.
    Intended to test machinary around processing data."""

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
