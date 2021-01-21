import os
from collections import defaultdict
from tempfile import TemporaryDirectory
from unittest import TestCase

import numpy as np

from watchopticalmc.internal.utils.cache import (
    Cache,
    cachedcall,
    cachedcallable,
    cacheget,
)
from watchopticalmc.internal.utils.filepathutils import temporaryworkingdirectory


def _dummyfunction():
    pass


class _DummyClass:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, _DummyClass) and other.value == self.value


class TestCache(TestCase):
    def createpurepython(self):
        return {
            "an int": 1,
            "a float": 2.0,
            "a string": "hello world",
            "a python list": [1, 2, 3, 4],
            "a python dict": {"a": 1, "b": 2},
            "a python set": {1, 2, 3, 4},
            "a function type": _dummyfunction,
            "a custom object": _DummyClass(1.0),
        }

    def createnumpyarray(self):
        return np.array([1.0, 2.0, 3.0])

    def createlambda(self):
        return lambda x: 2.0 * x

    def test_cache_read_write_python(self):
        with TemporaryDirectory() as dirname:
            dbname = os.sep.join((dirname, "test.db"))
            writevalue = self.createpurepython()

            # write
            with Cache(dbname) as cache:
                cache["key"] = writevalue
            # read
            with Cache(dbname) as cache:
                readvalue = cache["key"]

            self.assertEqual(writevalue, readvalue)

    def test_cache_read_write_lambda(self):
        with TemporaryDirectory() as dirname:
            dbname = os.sep.join((dirname, "test.db"))
            writevalue = self.createlambda()

            # write
            with Cache(dbname) as cache:
                cache["key"] = writevalue
            # read
            with Cache(dbname) as cache:
                readvalue = cache["key"]

            self.assertEqual(writevalue.__code__.co_code, readvalue.__code__.co_code)
            self.assertEqual(
                writevalue.__code__.co_consts, readvalue.__code__.co_consts
            )

    def test_cache_read_write_numpy_array(self):
        with TemporaryDirectory() as dirname:
            dbname = os.sep.join((dirname, "test.db"))
            writevalue = self.createnumpyarray()

            # write
            with Cache(dbname) as cache:
                cache["key"] = writevalue
            # read
            with Cache(dbname) as cache:
                readvalue = cache["key"]

            self.assertTrue(np.all(writevalue == readvalue))

    def test_cached_get(self):
        with temporaryworkingdirectory():
            writtenvalue = self.createpurepython()
            with Cache() as c:
                c["key"] = writtenvalue

            readvalue = cacheget("key")

            self.assertEqual(readvalue, writtenvalue)

    def test_cached_call(self):
        with temporaryworkingdirectory():
            callvalue = cachedcall("key", self.createpurepython)

            readvalue = cacheget("key")
            self.assertEqual(callvalue, readvalue)
            self.assertEqual(callvalue, self.createpurepython())

    def test_cached_callable(self):
        with temporaryworkingdirectory():
            callcount = defaultdict(int)

            @cachedcallable(lambda x: f"x_is_{x}")
            def triple(x, callcount=callcount):
                callcount[x] += 1
                return 3 * x

            result = (triple(1), triple(1), triple(2), triple(2))

            self.assertEqual(result, (3, 3, 6, 6))
            self.assertEqual(callcount, {1: 1, 2: 1})
