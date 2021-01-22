import glob
import os
import unittest
from tempfile import TemporaryDirectory

from watchopticalmc.internal.generatemc.runwatchmakers import (
    WatchMakersConfig,
    generatejobscripts,
)
from watchopticalmc.internal.generatemc.wmdataset import WatchmanDataset
from watchopticalutils.filepathutils import touchfile


class TestWMDataset(unittest.TestCase):
    def test_wmdataset(self):
        with TemporaryDirectory() as d:
            scripts = generatejobscripts(WatchMakersConfig(directory=d))
            directory = scripts.directory
            jobdirs = list(glob.glob(f"{directory}{os.sep}*root_files_*/*"))
            for d in jobdirs:
                touchfile(f"{d}{os.sep}runDUMMYFILE.root")

            dataset = WatchmanDataset(
                [f"{directory}{os.sep}*root_files_*{os.sep}*{os.sep}*.root"]
            )

            self.assertEqual(len(jobdirs) / 2, len(dataset))
            self.assertTrue(len(dataset) > 0)
        return
