import os
import unittest
from collections import OrderedDict

import dask.distributed

from watchoptical.internal.generatemc import GenerateMCConfig, generatemc
from watchoptical.internal.makeratdb import makeratdb
from watchoptical.internal.runwatchmakers import WatchMakersConfig


class TestGenerateMCWithTweakedOpticalModel(unittest.TestCase):
    def ratdb(self, attenuation):
        return makeratdb(attenuation=attenuation)

    def test_generatemc_withcustomattenuation(self):
        with dask.distributed.Client(
            n_workers=1, threads_per_worker=1, memory_limit="4GB"
        ):
            ratdb = OrderedDict(
                (f"attenuation_{index}", self.ratdb(attenuation))
                for index, attenuation in enumerate([1.0])
            )
            jobs = generatemc(
                GenerateMCConfig(
                    WatchMakersConfig(numevents=1),
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
