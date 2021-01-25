from watchopticalmc import AnalysisDataset
from watchopticalanalysis.internal.runopticsanalysis import runopticsanalysis
from watchopticalutils.filepathutils import temporaryworkingdirectory


def test_runopticsanalysis_completes_without_error(
    signaldatasetfixture: AnalysisDataset,
):
    with temporaryworkingdirectory():
        runopticsanalysis(signaldatasetfixture).compute()
