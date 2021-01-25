import os
import tempfile
import unittest
from tempfile import TemporaryDirectory

from watchopticalmc.internal.generatemc.generatemc import GenerateMCConfig, generatemc
from watchopticalmc.internal.generatemc.runwatchmakers import WatchMakersConfig
from watchopticalmc.internal.generatemc.runwatchmakerssensitivityanalysis import (
    WatchMakersSensitivityAnalysisConfig,
    runwatchmakerssensitivityanalysis,
)
from watchopticalutils.client import ClientType, client


class TestRunWatchMakersSensitivityAnalysis(unittest.TestCase):
    inputmcdirectory = (
        f"{tempfile.gettempdir()}"
        f"{os.sep}wm{os.sep}tmp{os.sep}"
        f"tmp_watchoptical_unittest_runwatchmakerssensitivityanalysis_"
        f"{os.getuid()}"
    )

    @classmethod
    def setUpClass(cls) -> None:
        cls.ensure_input_mc_exists()

    @classmethod
    def ensure_input_mc_exists(cls):
        if not os.path.exists(cls.inputmcdirectory):
            with client(ClientType.LOCAL):
                generatemc(
                    GenerateMCConfig(
                        WatchMakersConfig(numevents=1, directory=cls.inputmcdirectory),
                        numjobs=1,
                    )
                ).compute()
        return

    def test_runwatchmakerssensitvityanalysis_defaultconfiguration_generatesoutput(
        self,
    ):
        with TemporaryDirectory():
            config = WatchMakersSensitivityAnalysisConfig(
                inputdirectory=self.inputmcdirectory
            )
            runwatchmakerssensitivityanalysis(config)


if __name__ == "__main__":
    unittest.main()
