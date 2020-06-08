import glob
import os
import unittest

from watchoptical.internal import runwatchmakers
from watchoptical.internal.utils import touchfile
from watchoptical.internal.wmdataset import WatchmanDataset


class TestWMDataset(unittest.TestCase):
    def test_wmdataset(self):
        scripts = runwatchmakers.generatejobscripts()
        directory = scripts.directory
        jobdirs = list(glob.glob(f"{directory}{os.sep}*root_files_*/*"))
        filelist = list(map(lambda d: touchfile(f"{d}{os.sep}runDUMMYFILE.root"), jobdirs))

        dataset = WatchmanDataset([f"{directory}{os.sep}*root_files_*{os.sep}*{os.sep}*.root"])

        self.assertEqual(len(jobdirs) / 2, len(dataset.files))
        self.assertTrue(len(dataset.files) > 0)
        return
