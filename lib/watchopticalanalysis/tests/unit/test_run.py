from watchopticalanalysis.process import Algorithm, process
from watchopticalmc import AnalysisEventTuple
import dask.bag

class Unit(Algorithm[int]):
    def apply(self, data: AnalysisEventTuple) -> int:
        return 1
    
    def finish(self, result: int) -> None:
        print(f"DEBUG finish {result}")
        return result

def test_process():
    algs = [Unit(),]
    dataset = dask.bag.from_sequence([None, None, None, None])
    result = process(algs, dataset)
    assert result == (4, )