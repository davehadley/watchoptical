from typing import TypeVar, Callable, Generic, Iterable
from watchopticalmc import AnalysisEventTuple
from watchopticalutils.collectionutils import sumlist
from abc import ABC, abstractmethod
from dask.bag import Bag
import operator
from itertools import starmap

T = TypeVar('T')

class Algorithm(ABC, Generic[T]):
    @abstractmethod
    def apply(self, data: AnalysisEventTuple) -> T:
        pass
    
    @abstractmethod
    def finish(self, result: T) -> None:
        pass

def process(algorithms: Iterable[Algorithm], dataset: Bag, force: bool=False):
    def fold(*args, **kwargs):
        print(f"fold-> {args} {kwargs}")
        return tuple(left + right for left, right in zip(*args))
    def finish(*args, **kwargs):
        print(f"finish-> {args} {kwargs}")
        return tuple(alg.finish(r) for (alg, r) in zip(algorithms, args)) 
    reduced = (dataset
        .map(lambda data: tuple(alg.apply(data) for alg in algorithms))
        #.map(sumlist)
        #.reduction(lambda x: print(f"x is: {list(x)}"), lambda y: print(f"y is {list(y)}"))
        #.compute())
        #.reduction(lambda row: zip(*row), sumlist).compute())
        .fold(fold, out_type=Bag)
        .map(finish)
        )
    print("DEBUG", reduced)
    #tuple(alg.finish(result) for alg in algorithms)
    result = reduced.compute()
    assert len(result) == 1
    return result[0]