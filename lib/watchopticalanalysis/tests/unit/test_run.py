from subprocess import run

from watchopticalmc import AnalysisDataset
from watchopticalutils.filepathutils import temporaryworkingdirectory


def test_run_noop(signaldatasetfixture: AnalysisDataset):
    with temporaryworkingdirectory():
        run(
            [
                "python3",
                "-m",
                "watchopticalanalysis",
                str(signaldatasetfixture.directory),
                "--alg=test",
            ],
            check=True,
        )
