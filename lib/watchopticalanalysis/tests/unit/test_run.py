from subprocess import run

import pytest
from watchopticalanalysis.algs import AlgDefs
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
                "--client=single",
            ],
            check=True,
        )


@pytest.mark.parametrize("alg", list(AlgDefs))
def test_run_each_alg(signaldatasetfixture: AnalysisDataset, alg: AlgDefs):
    with temporaryworkingdirectory():
        run(
            [
                "python3",
                "-m",
                "watchopticalanalysis",
                str(signaldatasetfixture.directory),
                f"--alg={alg.name}",
                "--client=single",
            ],
            check=True,
        )
