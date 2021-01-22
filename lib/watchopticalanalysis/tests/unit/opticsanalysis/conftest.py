import os
import tempfile

import pytest

from watchopticalmc.internal.generatemc.generatemc import GenerateMCConfig, generatemc
from watchopticalmc.internal.generatemc.runwatchmakers import WatchMakersConfig
from watchopticalmc.internal.generatemc.wmdataset import WatchmanDataset
from watchopticalmc.internal.stringconstants import StringConstants
from watchopticalutils.client import ClientType, client
from watchopticalutils.filepathutils import (
    searchforrootfilesexcludinganalysisfiles,
)


@pytest.fixture(scope="module")
def signaldatasetfixture() -> WatchmanDataset:
    with client(ClientType.SINGLE):
        dirname = (
            f"{tempfile.gettempdir()}"
            f"{os.sep}wm{os.sep}tmp{os.sep}"
            "tmp_watchoptical_unittest_signaldataset"
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
