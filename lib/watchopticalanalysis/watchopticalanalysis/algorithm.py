from abc import ABC, abstractmethod
from typing import Generic, Iterable, Optional, Tuple, TypeVar

from dask.bag import Bag
from watchopticalmc import AnalysisEventTuple
from watchopticalutils.cache import Cache

T = TypeVar("T")
U = TypeVar("U")


class Algorithm(ABC, Generic[T, U]):
    @abstractmethod
    def apply(self, data: AnalysisEventTuple) -> T:
        pass

    @abstractmethod
    def finish(self, result: T) -> U:
        pass


def apply_algorithms(algorithms: Iterable[Algorithm], dataset: Bag) -> Tuple:
    algorithms = list(algorithms)

    def fold(*args, **kwargs):
        return tuple(left + right for left, right in zip(*args))

    def finish(*args, **kwargs):
        return tuple(alg.finish(r) for (alg, r) in zip(algorithms, args))

    reduced = (
        dataset.map(lambda data: tuple(alg.apply(data) for alg in algorithms))
        .fold(fold)
        .compute()
    )
    result = tuple(a.finish(r) for r, a in zip(reduced, algorithms))
    assert len(result) == len(algorithms)
    return result


def cached_apply_algorithms(
    algorithms: Iterable[Algorithm], dataset: Bag, cache: Optional[Cache] = None
) -> Tuple:
    # if cache is None:
    #    cache = Cache()
    return apply_algorithms(algorithms, dataset)
