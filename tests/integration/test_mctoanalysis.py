import glob
import os
import tempfile
import unittest

import dask.distributed

from watchoptical.internal.generatemc.generatemc import GenerateMCConfig, generatemc
from watchoptical.internal.generatemc.mctoanalysis import (
    MCToAnalysisConfig,
    mctoanalysis,
)
from watchoptical.internal.generatemc.runwatchmakers import WatchMakersConfig
from watchoptical.internal.generatemc.wmdataset import WatchmanDataset


class TestMCToAnalysis(unittest.TestCase):
    directory = (
        f"{tempfile.gettempdir()}{os.sep}tmp_watchoptical_unittest_testmctoanalysis"
    )
    filenamepattern = f"{directory}{os.sep}*{os.sep}*{os.sep}*.root"

    @classmethod
    def setUpClass(cls) -> None:
        if len(glob.glob(cls.filenamepattern)) == 0:
            # we need some MC file to work with
            with dask.distributed.Client(
                n_workers=1, threads_per_worker=1, memory_limit="4GB"
            ):
                generatemc(
                    GenerateMCConfig(
                        WatchMakersConfig(numevents=10, directory=cls.directory),
                        filenamefilter=lambda name: "IBD_LIQUID_pn" in name,
                    )
                ).compute()

    def test_mctoanalysis(self):
        with dask.distributed.Client(
            n_workers=1, threads_per_worker=1, memory_limit="1GB"
        ):
            dataset = WatchmanDataset([self.filenamepattern])
            config = MCToAnalysisConfig(directory=tempfile.mkdtemp())
            results = mctoanalysis(dataset, config).compute()
            self.assertTrue(len(results) > 0)
            self.assertTrue(all(os.path.exists(f.filename) for f in results))


if __name__ == "__main__":
    unittest.main()
