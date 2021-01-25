from watchopticalanalysis.process import Algorithm, process
from watchopticalmc import AnalysisEventTuple
import dask.bag
from typing import Any

class RetInt(Algorithm[int, int]):

    def __init__(self, value: int=1):
        super().__init__()
        self.value = value

    def apply(self, data: AnalysisEventTuple) -> int:
        return self.value
    
    def finish(self, result: int) -> int:
        return result

class Identity(Algorithm[Any, Any]):

    def apply(self, data: AnalysisEventTuple) -> Any:
        return data
    
    def finish(self, result: int) -> Any:
        return result

def test_process_no_alg():
    algs = []
    dataset = dask.bag.from_sequence([None, None, None, None])
    result = process(algs, dataset)
    assert result == tuple()

def test_process_one_alg():
    algs = [RetInt(),]
    dataset = dask.bag.from_sequence([1, 2, 3, 4])
    result = process(algs, dataset)
    assert result == (4, )

def test_process_two_alg():
    algs = [RetInt(1), RetInt(2),]
    dataset = dask.bag.from_sequence(["A", "B", "C", "D"])
    result = process(algs, dataset)
    assert result == (4, 8)

def test_process_two_alg_with_data():
    algs = [Identity(), Identity(),]
    dataset = dask.bag.from_sequence(["A", "B", "C", "D"])
    result = process(algs, dataset)
    assert result == ("ABCD", "ABCD")