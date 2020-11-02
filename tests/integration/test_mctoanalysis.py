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
        columns = [
            "pmt_t",
            "pmt_x",
            "pmt_y",
            "pmt_z",
            "mc_pdgcode",
            "mc_t_start",
            "mc_t_end",
            "mc_x_start",
            "mc_x_end",
            "mc_y_start",
            "mc_y_end",
            "mc_z_start",
            "mc_z_end",
        ]
        assert all([col in a.columns for a in anal for col in columns])
