from enum import Enum
from typing import Any, Callable, NamedTuple

from pandas import DataFrame
from toolz import identity


def _hascoincidence(data: DataFrame) -> Any:
    t = data.groupby("mcid")
    count = t.transform("count")
    dt = t.transform(lambda t: t.max() - t.min())
    return (count >= 2) & (dt.abs() < 50.0)


class Selection(NamedTuple):
    name: str
    f: Callable[[DataFrame], DataFrame]

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)


class SelectionDefs(Enum):
    nominal = Selection("nominal", lambda data: data[((data.closestPMT / 1500.0) > 1.0)
                                                     & (data.good_pos > 0.1)
                                                     & (data.inner_hit > 4)
                                                     & (data.veto_hit < 4)
                                                     & _hascoincidence(data)
                                                     ])

    noselection = Selection("noselection", lambda data: identity(data))
