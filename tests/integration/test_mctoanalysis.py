import glob
import os
import tempfile

import pytest

from watchoptical.internal.generatemc.generatemc import GenerateMCConfig, generatemc
from watchoptical.internal.generatemc.mctoanalysis import (
    MCToAnalysisConfig,
    mctoanalysis,
)
from watchoptical.internal.generatemc.runwatchmakers import WatchMakersConfig
from watchoptical.internal.generatemc.watchmakersfilenameutils import issignalfile
from watchoptical.internal.generatemc.wmdataset import WatchmanDataset
from watchoptical.internal.opticsanalysis.analysiseventtuple import AnalysisEventTuple
from watchoptical.internal.utils.client import ClientType, client


@pytest.fixture
def smallsignaldataset() -> WatchmanDataset:
    directory = (
        f"{tempfile.gettempdir()}"
        f"{os.sep}"
        f"tmp_watchoptical_unittest_testmctoanalysis"
    )
    filenamepattern = f"{directory}{os.sep}*{os.sep}*{os.sep}*.root"
    if len(glob.glob(filenamepattern)) == 0:
        with client(ClientType.LOCAL):
            generatemc(
                GenerateMCConfig(
                    WatchMakersConfig(numevents=10, directory=directory),
                    filenamefilter=issignalfile,
                )
            ).compute()
    return WatchmanDataset([filenamepattern])


def test_mctoanalysis(smallsignaldataset):
    with client(ClientType.SINGLE):
        config = MCToAnalysisConfig(directory=tempfile.mkdtemp())
        results = mctoanalysis(smallsignaldataset, config).compute()
        anal = [AnalysisEventTuple.load(f).anal for f in results]
        assert len(results) > 0
        assert all(os.path.exists(f.filename) for f in results)
        assert all("pmt_t" in a.columns for a in anal)
        assert all("pmt_x" in a.columns for a in anal)
        assert all("pmt_y" in a.columns for a in anal)
        assert all("pmt_z" in a.columns for a in anal)
