import pytest
from numpy import dtype

from watchopticalmc import AnalysisDataset, AnalysisEventTuple
from watchopticalanalysis.internal.selectiondefs import SelectionDefs


@pytest.mark.parametrize("selection", list(SelectionDefs))
def test_selection_does_not_raise_exception(
    signaldatasetfixture: AnalysisDataset, selection: SelectionDefs
):
    for et in AnalysisEventTuple.fromAnalysisDataset(signaldatasetfixture):
        selection.value(et.bonsai)


@pytest.mark.parametrize("selection", list(SelectionDefs))
def test_selection_cuts_return_correct_type(
    signaldatasetfixture: AnalysisDataset, selection: SelectionDefs
):
    for et in AnalysisEventTuple.fromAnalysisDataset(signaldatasetfixture):
        for cut in selection.value.cuts:
            result = cut.apply(et.bonsai)
            assert result.dtype == dtype("bool")
            assert len(result.shape) == 1
