from typing import TypeVar, Callable, Generic, Iterable
from watchopticalmc import AnalysisEventTuple
from watchopticalutils.collectionutils import sumlist
from abc import ABC, abstractmethod
from dask.bag import Bag
import operator
from itertools import starmap

T = TypeVar('T')
U = TypeVar('U')

class Algorithm(ABC, Generic[T, U]):
    @abstractmethod
    def apply(self, data: AnalysisEventTuple) -> T:
        pass
    
    @abstractmethod
    def finish(self, result: T) -> U:
        pass

def process(algorithms: Iterable[Algorithm], dataset: Bag, force: bool=False):
    algorithms = list(algorithms)
    def fold(*args, **kwargs):
        return tuple(left + right for left, right in zip(*args))
    def finish(*args, **kwargs):
        print(f"finish-> {args} {kwargs}")
        return tuple(alg.finish(r) for (alg, r) in zip(algorithms, args)) 
    reduced = (dataset
        .map(lambda data: tuple(alg.apply(data) for alg in algorithms))
        .fold(fold).compute())
    result = tuple(a.finish(r) for r, a in zip(reduced, algorithms))
    assert len(result) == len(algorithms)
    return result