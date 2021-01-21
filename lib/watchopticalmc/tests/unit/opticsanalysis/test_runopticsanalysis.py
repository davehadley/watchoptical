from watchoptical.internal.generatemc.wmdataset import WatchmanDataset
from watchoptical.internal.opticsanalysis.runopticsanalysis import runopticsanalysis
from watchoptical.internal.utils.filepathutils import temporaryworkingdirectory


def test_runopticsanalysis_completes_without_error(
    signaldatasetfixture: WatchmanDataset,
):
    with temporaryworkingdirectory():
        runopticsanalysis(signaldatasetfixture).compute()
