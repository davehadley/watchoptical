import os
import random
import unittest
from tempfile import TemporaryDirectory

import dask.distributed

from watchoptical.internal.generatemc.generatemc import GenerateMCConfig, generatemc
from watchoptical.internal.generatemc.runwatchmakers import WatchMakersConfig
from watchoptical.internal.generatemc.watchmakersfilenameutils import (
    isbackgroundfile,
    issignalfile,
)


class TestGenerateMC(unittest.TestCase):
    def test_generatemc_signal(self):
        with dask.distributed.Client(
            n_workers=1, threads_per_worker=1, memory_limit="4GB"
        ):
            with TemporaryDirectory() as d:
                jobs = generatemc(
                    GenerateMCConfig(
                        WatchMakersConfig(directory=d, numevents=1),
                        numjobs=1,
                        filenamefilter=issignalfile,
                    )
                )
                results = random.choice(jobs.to_delayed()).compute()
                self.assertTrue(len(results) > 0)
                self.assertTrue(all(os.path.exists(f) for r in results for f in r))

    @unittest.skip("Some backgrounds fail due to Watchmakers bugs.")
    def test_generatemc_background(self):
        with dask.distributed.Client(
            n_workers=1, threads_per_worker=1, memory_limit="4GB"
        ):
            with TemporaryDirectory() as d:
                jobs = generatemc(
                    GenerateMCConfig(
                        WatchMakersConfig(directory=d, numevents=1),
                        numjobs=1,
                        filenamefilter=isbackgroundfile,
                    )
                )
                # it is slow to run all so just pick a random background
                results = random.choice(jobs.to_delayed()).compute()
                # results = jobs.compute()
                self.assertTrue(len(results) > 0)
                self.assertTrue(all(os.path.exists(f) for r in results for f in r))


if __name__ == "__main__":
    unittest.main()
