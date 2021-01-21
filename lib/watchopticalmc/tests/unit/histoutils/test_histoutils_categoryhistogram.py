import unittest

import boost_histogram as bh
import numpy as np

from watchopticalmc.internal.histoutils import CategoryHistogram


class TestHistoUtilsCategoryHistogram(unittest.TestCase):
    def assertArrayEqual(self, a, b):
        return self.assertTrue(np.all(a == b))

    def test_categoryhistogram_fill(self):
        h = CategoryHistogram(bh.axis.Regular(3, 0.0, 3.0))
        h.fill("A", np.array([1.0]))
        h.fill("B", np.array([2.0]))
        d = dict(h)
        self.assertArrayEqual(d["A"].view(), np.array([0.0, 1.0, 0.0]))
        self.assertArrayEqual(d["B"].view(), np.array([0.0, 0.0, 1.0]))

    def test_categoryhistogram_sum(self):
        h1 = CategoryHistogram(bh.axis.Regular(3, 0.0, 3.0))
        h1.fill("A", np.array([1.0]))
        h1.fill("B", np.array([2.0]))
        h2 = CategoryHistogram(bh.axis.Regular(3, 0.0, 3.0))
        h2.fill("A", np.array([1.0]))
        h2.fill("B", np.array([2.0]))

        h = h1 + h2

        d = dict(h)
        self.assertArrayEqual(d["A"].view(), np.array([0.0, 2.0, 0.0]))
        self.assertArrayEqual(d["B"].view(), np.array([0.0, 0.0, 2.0]))
