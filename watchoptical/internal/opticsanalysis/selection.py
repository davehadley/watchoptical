import operator
from enum import Enum
from functools import reduce
from typing import Callable, NamedTuple, Tuple

from pandas import DataFrame, Series
from toolz import identity


def _hascoincidence(data: DataFrame) -> Series:
    t = data.groupby("mcid")
    count = t.transform("count")
    dt = t.transform(lambda t: t.max() - t.min())
    return (count >= 2) & (dt.abs() < 50.0)


def _fiducialvolumecut(data: DataFrame) -> Series:
    return (data.closestPMT / 1500.0) > 1.0


def _goodpositioncut(data: DataFrame) -> Series:
    return data.good_pos > 0.1


def _innerhitscut(data: DataFrame) -> Series:
    return data.inner_hit > 4


def _vetohitscut(data: DataFrame) -> Series:
    return data.veto_hit < 4


class Selection(NamedTuple):
    name: str
    cuts: Tuple[Callable[[DataFrame], Series], ...]

    def select(self, data: DataFrame) -> DataFrame:
        selected = reduce(operator.and_, (c(data) for c in self.cuts))
        return data[selected]

    def __call__(self, *args, **kwargs):
        return self.select(*args, **kwargs)


class SelectionDefs(Enum):
    nominal = Selection(
        name="nominal",
        cuts=(
            _fiducialvolumecut,
            _goodpositioncut,
            _innerhitscut,
            _vetohitscut,
            _hascoincidence,
        ),
    )

    noselection = Selection(name="noselection", cuts=(identity,))
