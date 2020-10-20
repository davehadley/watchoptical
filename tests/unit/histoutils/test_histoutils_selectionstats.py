import unittest

import numpy as np
from pandas import DataFrame

from watchoptical.internal.histoutils.cut import Cut
from watchoptical.internal.histoutils.selection import Selection
from watchoptical.internal.histoutils.selectionstats import SelectionStats


class TestSelectionStats(unittest.TestCase):
    _random = np.random.RandomState(1234)

    def _sampledata(self):
        return DataFrame(
            data=self._random.normal([0.0, 0.0], [1.0, 1.0], size=(100, 2)),
            columns=["x", "y"],
        )

    def _sampleselection(self):
        return Selection(
            name="Simple selection",
            cuts=(Cut(lambda d: d.x > 0.0), Cut(lambda d: d.y < 0.0)),
        )

    def test_selectionstats(self):
        stat = SelectionStats(self._sampleselection())

        stat.fill(self._sampledata())

        self.assertAlmostEqual(stat[0].efficiency, 0.5, delta=0.01)
