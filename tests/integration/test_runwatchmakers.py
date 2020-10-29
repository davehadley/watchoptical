import os
import unittest
from tempfile import TemporaryDirectory

from watchoptical.internal.generatemc import runwatchmakers
from watchoptical.internal.generatemc.runwatchmakers import (
    WatchMakersConfig,
    generatejobscripts,
)


class TestRunWatchMakers(unittest.TestCase):
    def test_watchoptical_imports_without_error(self):
        import watchoptical

        self.assertTrue(watchoptical)

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
