from tempfile import NamedTemporaryFile
from typing import Any, Optional

import dask.bag
from watchopticalanalysis.algorithm import (
    Algorithm,
    apply_algorithms,
    cached_apply_algorithms,
)
from watchopticalmc import AnalysisEventTuple
from watchopticalutils.cache import Cache
from watchopticalutils.client import ClientType, client

# from watchopticalutils.client import Client, client


class RetInt(Algorithm[int, int]):
    def __init__(self, value: int = 1):
        super().__init__()
        self.value = value

    def apply(self, data: AnalysisEventTuple) -> int:
        return self.value

    def finish(self, result: int) -> int:
        return result


class Identity(Algorithm[Any, Any]):
    def __init__(self, key: str = None):
        self._key = key
        super().__init__()
        self.apply_count = 0
        self.finish_count = 0

    def key(self) -> Optional[str]:
        return self._key

    def apply(self, data: AnalysisEventTuple) -> Any:
        self.apply_count += 1
        return data

    def finish(self, result: int) -> Any:
        self.finish_count += 1
        return result


def test_process_no_alg():
    algs = []
    dataset = dask.bag.from_sequence([None, None, None, None])
    result = apply_algorithms(algs, dataset)
    assert result == tuple()


def test_process_one_alg():
    algs = [
        RetInt(),
    ]
    dataset = dask.bag.from_sequence([1, 2, 3, 4])
    result = apply_algorithms(algs, dataset)
    assert result == (4,)


def test_process_two_alg():
    algs = [
        RetInt(1),
        RetInt(2),
    ]
    dataset = dask.bag.from_sequence(["A", "B", "C", "D"])
    result = apply_algorithms(algs, dataset)
    assert result == (4, 8)


def test_process_two_alg_with_data():
    algs = [
        Identity(),
        Identity(),
    ]
    dataset = dask.bag.from_sequence(["A", "B", "C", "D"])
    result = apply_algorithms(algs, dataset)
    assert result == ("ABCD", "ABCD")


def test_cached_algorithm():
    with client(ClientType.SINGLE):
        with NamedTemporaryFile() as f:
            cache = Cache(f.name)
            algs1 = [Identity("k1"), Identity("k2")]
            dataset = dask.bag.from_sequence(["A", "B", "C", "D"])
            result1 = cached_apply_algorithms(algs1, dataset, cache=cache)
            algs2 = [Identity("k1"), Identity("k2")]
            result2 = cached_apply_algorithms(algs2, dataset, cache=cache)
            assert all(
                [
                    algs1[0].apply_count == 4,
                    algs1[1].apply_count == 4,
                    algs2[0].apply_count == 0,
                    algs2[1].apply_count == 0,
                    algs1[0].finish_count == 1,
                    algs1[1].finish_count == 1,
                    algs2[0].finish_count == 1,
                    algs2[1].finish_count == 1,
                ]
            )
            assert result1 == result2
