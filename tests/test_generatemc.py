import re
import unittest

import dask.distributed
from dask.bag import random
from toolz import pipe, curry

from watchoptical.generatemc import generatemc, GenerateMCConfig
from watchoptical.runwatchmakers import WatchMakersConfig


class TestGenerateMC(unittest.TestCase):
    def test_generatemc(self):
        with dask.distributed.Client(n_workers=1,
                                     threads_per_worker=1,
                                     memory_limit='4GB'):
            jobs = generatemc(GenerateMCConfig(WatchMakersConfig(numevents=1)))
            # it is slow to run all so just pick one
            random.choice(jobs.to_delayed()).compute()


if __name__ == '__main__':
    unittest.main()
