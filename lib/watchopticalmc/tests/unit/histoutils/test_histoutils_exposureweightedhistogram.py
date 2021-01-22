import unittest

import boost_histogram as bh
import numpy as np

from watchopticalmc.internal.histoutils import ExposureWeightedHistogram


class TestHistoUtilsExposureWeightedHistogram(unittest.TestCase):
    def assertArrayEqual(self, a, b, msg=None):
        return self.assertTrue(
            np.all(a == b), msg if msg else f"arrays not equal: {a} != {b}"
        )

    def test_categoryhistogram_fill(self):
        h = ExposureWeightedHistogram(bh.axis.Regular(3, 0.0, 3.0))
        h.fill("A", 0.5, np.array([1.0]))
        h.fill("B", 2.0, np.array([2.0]))
        d = {item.category: item.histogram for item in h}
        self.assertArrayEqual(d["A"].view(), np.array([0.0, 2.0, 0.0]))
        self.assertArrayEqual(d["B"].view(), np.array([0.0, 0.0, 0.5]))

    def test_categoryhistogram_sum(self):
        h1 = ExposureWeightedHistogram(bh.axis.Regular(3, 0.0, 3.0))
        h1.fill("A", 0.5, np.array([1.0]))
        h1.fill("B", 2.0, np.array([2.0]))
        h2 = ExposureWeightedHistogram(bh.axis.Regular(3, 0.0, 3.0))
        h2.fill("A", 1.0, np.array([1.0]))
        h2.fill("B", 4.0, np.array([2.0]))

        h = h1 + h2

        d = {item.category: item.histogram for item in h}
        self.assertArrayEqual(d["A"].view(), np.array([0.0, 2.0 / 1.5, 0.0]))
        self.assertArrayEqual(d["B"].view(), np.array([0.0, 0.0, 2.0 / 6.0]))
