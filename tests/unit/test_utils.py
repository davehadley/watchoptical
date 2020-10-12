import os
import unittest
from shutil import rmtree
from tempfile import mkdtemp

from watchoptical.internal.utils import findfiles


class TestUtils(unittest.TestCase):
    def test_expandfilepatterns(self):
        tmpdirname = mkdtemp()
        try:
            expected = [f"{tmpdirname}{os.sep}{ii}.txt" for ii in range(3)]
            for f in expected:
                with open(f, "w"):
                    pass

            actual = findfiles([f"{tmpdirname}{os.sep}*.txt"])

            self.assertEqual(expected, actual)
        finally:
            rmtree(tmpdirname)
