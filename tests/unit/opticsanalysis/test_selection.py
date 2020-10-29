import pytest
from numpy import dtype

from watchoptical.internal.generatemc.wmdataset import WatchmanDataset
from watchoptical.internal.opticsanalysis.analysiseventtuple import AnalysisEventTuple
from watchoptical.internal.opticsanalysis.selectiondefs import SelectionDefs


@pytest.mark.parametrize("selection", list(SelectionDefs))
def test_selection_does_not_raise_exception(
    signaldatasetfixture: WatchmanDataset, selection: SelectionDefs
):
    for et in AnalysisEventTuple.fromWatchmanDataset(signaldatasetfixture):
        selection.value(et.bonsai)


@pytest.mark.parametrize("selection", list(SelectionDefs))
def test_selection_cuts_return_correct_type(
    signaldatasetfixture: WatchmanDataset, selection: SelectionDefs
):
    for et in AnalysisEventTuple.fromWatchmanDataset(signaldatasetfixture):
        for cut in selection.value.cuts:
            result = cut.apply(et.bonsai)
            assert result.dtype == dtype("bool")
            assert len(result.shape) == 1
