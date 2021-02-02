from watchopticalutils.filepathutils import temporaryworkingdirectory
from subprocess import run
import numpy as np
import uproot

def test_zeroatt_gives_no_light():
    with temporaryworkingdirectory() as dir:
        run(["/root/watchoptical/env/watchoptical/bin/python", "-m", "watchopticalmc", "--num-jobs=1", "--num-events-per-job=10", "--attenuation=0.0", "--client=single", "--signal-only", f"--directory={dir}"])
        qmean = np.average(np.concatenate(uproot.lazyarray("watchopticalanalysis*.root", "watchopticalanalysis", "total_charge")))
        breakpoint()
        assert qmean < 10.0