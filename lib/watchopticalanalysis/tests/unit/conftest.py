import os
import subprocess
import tempfile
from pathlib import Path

import pytest
from watchopticalmc import AnalysisDataset
from watchopticalutils.client import ClientType, client


@pytest.fixture()
def signaldatasetfixture() -> AnalysisDataset:
    with client(ClientType.SINGLE):
        dirname = (
            f"{tempfile.gettempdir()}"
            f"{os.sep}wm{os.sep}tmp{os.sep}"
            "tmp_watchoptical_unittest_signaldataset_2"
        )
        if not os.path.exists(dirname):
            subprocess.run(
                [
                    "python",
                    "-m",
                    "watchopticalmc",
                    "--signal-only",
                    "--num-events-per-job=20",
                    "--num-jobs=1",
                    "--client=local",
                    f"--directory={dirname}",
                ]
            )
    return AnalysisDataset.load(Path(dirname) / "analysisdataset.pickle")
