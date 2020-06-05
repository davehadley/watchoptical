import os
import unittest

from watchoptical import runwatchmakers


class TestRunWatchMakers(unittest.TestCase):
    def test_watchoptical_imports_without_error(self):
        import watchoptical
        self.assertTrue(watchoptical)

    def test_environment(self):
        self.assertTrue(os.path.exists(runwatchmakers.path_to_watchmakers_script()))

    def test_rundefaultconfiguration(self):
        output = runwatchmakers.generatejobscripts()
        self.assertGreater(len(output.scripts), 0, "runwatchmakers did not generate any job scripts.")
        self.assertTrue(all(os.path.exists(s) for s in output.scripts))


if __name__ == '__main__':
    unittest.main()
