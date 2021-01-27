from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory

import pytest
from watchopticalanalysis.algs import AlgDefs
from watchopticalmc import AnalysisDataset


def test_run_timestamp(signaldatasetfixture: AnalysisDataset):
    with TemporaryDirectory() as dir:
        run(
            [
                "python3",
                "-m",
                "watchopticalanalysis",
                str(signaldatasetfixture.directory),
                "--alg=timestamp",
                "--client=single",
                f"--output={dir}",
            ],
            check=True,
        )
        assert (Path(dir) / "plots" / "timestamp.txt").exists()


@pytest.mark.parametrize("alg", list(AlgDefs))
def test_run_each_alg(signaldatasetfixture: AnalysisDataset, alg: AlgDefs):
    with TemporaryDirectory() as dir:
        run(
            [
                "python3",
                "-m",
                "watchopticalanalysis",
                str(signaldatasetfixture.directory),
                f"--alg={alg.name}",
                "--client=single",
                f"--output={dir}",
            ],
            check=True,
        )
        assert (Path(dir) / "plots").exists()
        # check it creates at least 1 new file
        assert next((Path(dir) / "plots").glob("**/*"))
