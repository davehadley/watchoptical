import os
import unittest
from collections import OrderedDict
from tempfile import TemporaryDirectory

import dask.distributed

from watchoptical.internal.generatemc.generatemc import GenerateMCConfig, generatemc
from watchoptical.internal.generatemc.makeratdb import makeratdb
from watchoptical.internal.generatemc.runwatchmakers import WatchMakersConfig


class TestGenerateMCWithTweakedOpticalModel(unittest.TestCase):
    def ratdb(self, attenuation, scattering):
        return makeratdb(attenuation=attenuation, scattering=scattering)

    def test_generatemc_withcustomattenuation(self):
        with dask.distributed.Client(
            n_workers=1, threads_per_worker=1, memory_limit="4GB"
        ):
            ratdb = OrderedDict({"tweak_attenuation_and_scat": self.ratdb(1.1, 1.2)})
            with TemporaryDirectory() as d:
                jobs = generatemc(
                    GenerateMCConfig(
                        WatchMakersConfig(directory=d, numevents=1),
                        numjobs=1,
                        filenamefilter=lambda f: "IBD_LIQUID_pn" in f,
                        injectratdb=ratdb,
                    )
                )
                results = jobs.compute()
                self.assertTrue(len(results) > 0)
                self.assertTrue(all(os.path.exists(f) for r in results for f in r))


if __name__ == "__main__":
    unittest.main()
