import os
import unittest

from watchoptical import runwatchmakers


class TestRunWatchMakers(unittest.TestCase):
    def test_watchoptical_imports_without_error(self):
        import watchoptical
        self.assertTrue(watchoptical)

    def test_environment(self):
        self.assertTrue(os.path.exists(runwatchmakers.path_to_watchmakers_script()))


if __name__ == '__main__':
    unittest.main()
