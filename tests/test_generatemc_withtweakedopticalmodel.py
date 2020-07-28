import inspect
import os
import random
import re
import unittest
from collections import OrderedDict

import dask.distributed
from toolz import pipe, curry

from watchoptical.internal.generatemc import generatemc, GenerateMCConfig
from watchoptical.internal.ratmacro import ratmacro
from watchoptical.internal.runwatchmakers import WatchMakersConfig


class TestGenerateMC(unittest.TestCase):

    def macro(self, attenuation):
        return ratmacro(attenuation=attenuation)

    def test_generatemc_withcustomattenuation(self):
        with dask.distributed.Client(n_workers=1,
                                     threads_per_worker=1,
                                     memory_limit='4GB'):
            macros = OrderedDict((f"attenuation_{index}", self.macro(attenuation)) for index, attenuation in enumerate([1.0, 10.0, 100.0, 10e3]))
            jobs = generatemc(GenerateMCConfig(WatchMakersConfig(numevents=1), numjobs=1,
                                               filenamefilter=lambda f: "IBD_LIQUID_pn" in f,
                                               injectmacros=macros,
                                               ))
            results = jobs.compute()
            self.assertTrue(len(results)>0)
            self.assertTrue(all(os.path.exists(f) for r in results for f in r))



if __name__ == '__main__':
    unittest.main()
