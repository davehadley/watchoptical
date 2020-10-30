import os
import tempfile

import pytest

from watchoptical.internal.generatemc.generatemc import GenerateMCConfig, generatemc
from watchoptical.internal.generatemc.runwatchmakers import WatchMakersConfig
from watchoptical.internal.generatemc.wmdataset import WatchmanDataset
from watchoptical.internal.stringconstants import StringConstants
from watchoptical.internal.utils.client import ClientType, client
from watchoptical.internal.utils.filepathutils import (
    searchforrootfilesexcludinganalysisfiles,
)


@pytest.fixture(scope="module")
def signaldatasetfixture() -> WatchmanDataset:
    with client(ClientType.SINGLE):
        dirname = (
            f"{tempfile.gettempdir()}{os.sep}tmp_watchoptical_unittest_signaldataset"
        )
        if not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
            generatemc(
                GenerateMCConfig(
                    WatchMakersConfig(directory=dirname, numevents=20),
                    numjobs=1,
                    filenamefilter=lambda n: StringConstants.WATCHMAKERS_SIGNAL_PATTERN
                    in n,
                )
            ).compute()
    return WatchmanDataset(searchforrootfilesexcludinganalysisfiles([dirname]))
