import os
import random
import re
import unittest

import dask.distributed
from toolz import pipe, curry

from watchoptical.internal.generatemc import generatemc, GenerateMCConfig
from watchoptical.internal.runwatchmakers import WatchMakersConfig


class TestGenerateMC(unittest.TestCase):
    def test_generatemc(self):
        with dask.distributed.Client(n_workers=1,
                                     threads_per_worker=1,
                                     memory_limit='4GB'):
            jobs = generatemc(GenerateMCConfig(WatchMakersConfig(numevents=1), numjobs=1))
            # it is slow to run all so just pick one
            results = random.choice(jobs.to_delayed()).compute()
            self.assertTrue(len(results)>0)
            self.assertTrue(all(os.path.exists(f) for r in results for f in r))


if __name__ == '__main__':
    unittest.main()
