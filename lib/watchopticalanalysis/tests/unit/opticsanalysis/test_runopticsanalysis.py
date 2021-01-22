from watchopticalmc.internal.generatemc.wmdataset import WatchmanDataset
from watchopticalanalysis.internal.runopticsanalysis import runopticsanalysis
from watchopticalutils.filepathutils import temporaryworkingdirectory


def test_runopticsanalysis_completes_without_error(
    signaldatasetfixture: WatchmanDataset,
):
    with temporaryworkingdirectory():
        runopticsanalysis(signaldatasetfixture).compute()
