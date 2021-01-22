import unittest

import numpy as np
from pandas import DataFrame

from watchopticalanalysis.internal.histoutils.cut import Cut
from watchopticalanalysis.internal.histoutils.selection import Selection


class TestSelection(unittest.TestCase):
    def test_selection(self):
        data = DataFrame(
            data=np.random.normal([0.0, 0.0], [1.0, 1.0], size=(100, 2)),
            columns=["x", "y"],
        )

        sel = Selection(
            name="Simple selection",
            cuts=(Cut(lambda d: d.x > 0.0), Cut(lambda d: d.y < 0.0)),
        )
        selected = sel(data)
        self.assertTrue(selected.equals(data[(data.x > 0.0) & (data.y < 0.0)]))
