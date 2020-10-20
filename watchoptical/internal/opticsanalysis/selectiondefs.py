from enum import Enum

import numpy as np
from pandas import DataFrame, Series

from watchoptical.internal.histoutils.cut import Cut
from watchoptical.internal.histoutils.selection import Selection


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


def _passall(data: DataFrame) -> Series:
    return Series(np.ones(shape=data.size, dtype=bool))


class SelectionDefs(Enum):
    nominal = Selection(
        name="nominal",
        cuts=(
            Cut(_fiducialvolumecut),
            Cut(_goodpositioncut),
            Cut(_innerhitscut),
            Cut(_vetohitscut),
            Cut(_hascoincidence),
        ),
    )

    noselection = Selection(name="noselection", cuts=(Cut(_passall),))
