import unittest


class TestWatchOpticalPackage(unittest.TestCase):
    def test_watchoptical_imports_without_error(self):
        import watchoptical

        self.assertTrue(watchoptical)


if __name__ == "__main__":
    unittest.main()
