import logging
from abc import ABC, abstractmethod
from typing import Generic, Iterable, Optional, Tuple, TypeVar

from dask.bag import Bag
from watchopticalmc import AnalysisEventTuple
from watchopticalutils.cache import Cache

T = TypeVar("T")
U = TypeVar("U")

_log = logging.getLogger(__name__)


class Algorithm(ABC, Generic[T, U]):
    def key(self) -> Optional[str]:
        """Unique key used to retrieve from cache."""
        return None

    @abstractmethod
    def apply(self, data: AnalysisEventTuple) -> T:
        pass

    @abstractmethod
    def finish(self, result: T) -> U:
        pass


def apply_algorithms(algorithms: Iterable[Algorithm], dataset: Bag) -> Tuple:
    return _run_finish(algorithms, _run_apply(algorithms, dataset))


def _run_apply(algorithms: Iterable[Algorithm], dataset: Bag) -> Tuple:
    algorithms = list(algorithms)

    def fold(*args):
        return tuple(left + right for left, right in zip(*args))

    reduced = (
        dataset.map(lambda data: tuple(alg.apply(data) for alg in algorithms))
        .fold(fold)
        .compute()
    )
    assert len(reduced) == len(algorithms)
    return tuple(reduced)


def _run_finish(algorithms: Iterable[Algorithm], reduced: Tuple) -> Tuple:
    def logfinish(r, a):
        _log.info(f"finalizing {a}")
        return a.finish(r)

    result = tuple(logfinish(r, a) for r, a in zip(reduced, algorithms))
    return result


def cached_apply_algorithms(
    algorithms: Iterable[Algorithm],
    dataset: Bag,
    cache: Optional[Cache] = None,
    force: bool = False,
) -> Tuple:
    algmap = {k: v for k, v in enumerate(algorithms)}
    result = {}
    notcached = {}
    if cache is None:
        cache = Cache()
    with cache as db:
        for k, v in algmap.items():
            try:
                if force:
                    raise KeyError
                result[k] = db[v.key()]
                _log.info(f"using cached results for {v}")
            except KeyError:
                notcached[k] = v
                _log.info(f"scheduling computation for {v}")
    notcached = tuple(notcached.items())
    # compute results that have not cached value
    newresults = _run_apply((v for _, v in notcached), dataset)
    # write the new results back to the cache
    with cache as db:
        for ((k, v), r) in zip(notcached, newresults):
            db[v.key()] = r
            result[k] = r
    # return the result in the correct format
    _log.info("finalizing results")
    return _run_finish(algorithms, tuple(v for _, v in sorted(result.items())))
