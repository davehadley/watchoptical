from enum import Enum

import numpy as np
from pandas import DataFrame, Series

from watchopticalutils.histoutils.cut import Cut
from watchopticalutils.histoutils.selection import Selection


def _hascoincidence(data: DataFrame) -> Series:
    grp = data.groupby("mcid")
    count = grp["mcid"].transform("count")
    dt = grp["t"].transform(lambda t: t.max() - t.min())
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
            Cut(_fiducialvolumecut, "In FV"),
            Cut(_goodpositioncut, "Has good position"),
            Cut(_innerhitscut, "Inner hits"),
            Cut(_vetohitscut, "Veto hits"),
            Cut(_hascoincidence, "Coincidence"),
        ),
    )

    noselection = Selection(name="noselection", cuts=(Cut(_passall),))
