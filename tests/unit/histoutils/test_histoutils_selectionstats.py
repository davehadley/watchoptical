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
            data=self._random.normal([0.0, 0.0, 1.0], [1.0, 1.0, 0.1], size=(10000, 3)),
            columns=["x", "y", "w"],
        )

    def _sampleselection(self):
        return Selection(
            name="Simple selection",
            cuts=(Cut(lambda d: d.x > 0.0), Cut(lambda d: d.y < 0.0)),
        )

    def test_selectionstats_unweighted_individual(self):
        data = self._sampledata()

        stat = SelectionStats(self._sampleselection())

        stat.fill(data)

        np.testing.assert_almost_equal(
            [
                stat[0].individual.numtotal,
                stat[0].individual.numpassed,
                stat[0].individual.numfailed,
                stat[0].individual.efficiency,
                stat[1].individual.numtotal,
                stat[1].individual.numpassed,
                stat[1].individual.numfailed,
                stat[1].individual.efficiency,
            ],
            [
                len(data),
                np.sum(data.x > 0),
                np.sum(data.x < 0),
                np.sum(data.x > 0) / len(data),
                len(data),
                np.sum(data.y < 0),
                np.sum(data.y > 0),
                np.sum(data.y < 0) / len(data),
            ],
        )

    def test_selectionstats_unweighted_cumulative(self):
        data = self._sampledata()

        stat = SelectionStats(self._sampleselection())

        stat.fill(data)

        np.testing.assert_almost_equal(
            [
                stat[0].cumulative.numtotal,
                stat[0].cumulative.numpassed,
                stat[0].cumulative.numfailed,
                stat[0].cumulative.efficiency,
                stat[1].cumulative.numtotal,
                stat[1].cumulative.numpassed,
                stat[1].cumulative.numfailed,
                stat[1].cumulative.efficiency,
            ],
            [
                len(data),
                np.sum(data.x > 0),
                np.sum(data.x < 0),
                np.sum(data.x > 0) / len(data),
                len(data),
                np.sum(np.logical_and(data.y < 0, data.x > 0)),
                np.sum(np.logical_or(data.y > 0, data.x < 0)),
                np.sum(np.logical_and(data.y < 0, data.x > 0)) / len(data),
            ],
        )

    def test_selectionstats_floatweighted_individual(self):
        data = self._sampledata()

        stat = SelectionStats(self._sampleselection())

        w = 0.1
        stat.fill(data, w)

        np.testing.assert_almost_equal(
            [
                stat[0].individual.numtotal,
                stat[0].individual.numpassed,
                stat[0].individual.numfailed,
                stat[0].individual.efficiency,
                stat[1].individual.numtotal,
                stat[1].individual.numpassed,
                stat[1].individual.numfailed,
                stat[1].individual.efficiency,
            ],
            [
                len(data) * w,
                np.sum(data.x > 0) * w,
                np.sum(data.x < 0) * w,
                np.sum(data.x > 0) / len(data),
                len(data) * w,
                np.sum(data.y < 0) * w,
                np.sum(data.y > 0) * w,
                np.sum(data.y < 0) / len(data),
            ],
        )

    def test_selectionstats_arrayweighted_individual(self):
        data = self._sampledata()

        stat = SelectionStats(self._sampleselection())

        w = data.w
        stat.fill(data, w)

        np.testing.assert_almost_equal(
            [
                stat[0].individual.numtotal,
                stat[0].individual.numpassed,
                stat[0].individual.numfailed,
                stat[0].individual.efficiency,
                stat[1].individual.numtotal,
                stat[1].individual.numpassed,
                stat[1].individual.numfailed,
                stat[1].individual.efficiency,
            ],
            [
                np.sum(w),
                np.sum(w * (data.x > 0)),
                np.sum(w * (data.x < 0)),
                np.sum(w * (data.x > 0)) / np.sum(w),
                np.sum(w),
                np.sum(w * (data.y < 0)),
                np.sum(w * (data.y > 0)),
                np.sum(w * (data.y < 0)) / np.sum(w),
            ],
        )

    def test_selectionstats_stringrepresentation(self):
        data = self._sampledata()
        stat = SelectionStats(self._sampleselection())
        stat.fill(data)
        print(stat)
