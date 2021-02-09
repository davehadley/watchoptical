from subprocess import run

import numpy as np
import uproot
from watchopticalutils.filepathutils import temporaryworkingdirectory


def test_zeroatt_gives_no_light():
    with temporaryworkingdirectory() as dir:
        run(
            [
                "python",
                "-m",
                "watchopticalmc",
                "--num-jobs=1",
                "--num-events-per-job=10",
                "--attenuation=0.0",
                "--client=single",
                "--signal-only",
                f"--directory={dir}",
            ]
        )
        total_charge = np.sum(
            np.concatenate(
                uproot.lazyarray(
                    "watchopticalanalysis*.root", "watchopticalanalysis", "total_charge"
                )
            )
        )
        assert total_charge < 10.0
