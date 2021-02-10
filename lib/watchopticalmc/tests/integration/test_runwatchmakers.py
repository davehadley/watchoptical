import os
import unittest
from tempfile import TemporaryDirectory

from watchopticalmc.internal.generatemc import runwatchmakers
from watchopticalmc.internal.generatemc.runwatchmakers import (
    WatchMakersConfig,
    generatejobscripts,
)


class TestRunWatchMakers(unittest.TestCase):
    def test_watchoptical_imports_without_error(self):
        import watchopticalmc

        self.assertTrue(watchopticalmc)

    def test_environment(self):
        self.assertTrue(os.path.exists(runwatchmakers.path_to_watchmakers_script()))

    def test_rundefaultconfiguration(self):
        with TemporaryDirectory() as d:
            output = generatejobscripts(WatchMakersConfig(directory=d))
            self.assertGreater(
                len(output.scripts),
                0,
                "runwatchmakers did not generate any job scripts.",
            )
            self.assertTrue(all(os.path.exists(s) for s in output.scripts))


if __name__ == "__main__":
    unittest.main()
