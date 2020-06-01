import unittest

import dask.distributed

from watchoptical.generatemc import generatemc, GenerateMCConfig
from watchoptical.runwatchmakers import WatchMakersConfig


class TestGenerateMC(unittest.TestCase):
    def test_generatemc(self):
        #with dask.config.set(scheduler='single-threaded'):
        with dask.distributed.Client(n_workers=1,
               threads_per_worker=1,
               memory_limit='4GB'):
            generatemc(GenerateMCConfig(WatchMakersConfig(numevents=1))).compute()


if __name__ == '__main__':
    unittest.main()
