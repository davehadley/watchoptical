from watchopticalutils.filepathutils import temporaryworkingdirectory
from subprocess import run
from pathlib import Path
from watchopticalmc import AnalysisDataset


def test_runall():
    with temporaryworkingdirectory() as d:
        run(
            [
                "python",
                "-m",
                "watchopticalmc",
                "--signal-only",
                "--num-events-per-job=10",
                "--num-jobs=1",
                "--client=single",
            ],
            check=True,
        )
        path = Path(d) / "analysisdataset.pickle"
        assert AnalysisDataset.load(path)
    return
