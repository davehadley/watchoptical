from enum import Enum
from typing import Any, Callable, NamedTuple

import numpy as np
from boost_histogram.axis import Axis, Regular
from pandas import DataFrame
from watchopticalmc import AnalysisEventTuple


class AnalysisVariable(NamedTuple):
    name: str
    binning: Axis
    f: Callable[[AnalysisEventTuple], Any]

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)


class BonsaiVariable(NamedTuple):
    name: str
    binning: Axis
    f: Callable[[DataFrame], Any]

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)

    def into_analysis_variable(self) -> AnalysisVariable:
        f = self.f

        def _wrapped_f(data: AnalysisEventTuple) -> np.ndarray:
            return np.asarray(f(data.bonsai))

        return AnalysisVariable(
            self.name,
            self.binning,
            _wrapped_f,
        )


def _total_charge(data: AnalysisEventTuple) -> np.ndarray:
    return data.anal.total.total_charge.groupby("entry").nth(0).array


class BonsaiVariableDefs(Enum):
    eventcount = BonsaiVariable(
        "eventcount", Regular(1, 0.0, 1.0), lambda x: np.zeros(len(x))
    )
    n9 = BonsaiVariable("n9", Regular(26, 0.0, 60.0), lambda x: x.n9)
    innerPE = BonsaiVariable("innerPE", Regular(100, 0.0, 100.0), lambda x: x.innerPE)
    mcenergy = BonsaiVariable(
        "mcenergy", Regular(100, 0.0, 10.0), lambda x: x.mc_energy
    )
    innerPE_over_mcenergy = BonsaiVariable(
        "innerPE_over_mcenergy",
        Regular(100, 0.0, 50.0),
        lambda x: x.innerPE / x.mc_energy,
    )

    recox = BonsaiVariable("recox", Regular(100, -8000.0, 8000.0), lambda x: x.x)
    recoy = BonsaiVariable("recoy", Regular(100, -8000.0, 8000.0), lambda x: x.y)
    recoz = BonsaiVariable("recoz", Regular(100, -8000.0, 8000.0), lambda x: x.z)
    recot = BonsaiVariable("recot", Regular(100, -100.0, 10.0), lambda x: x.t)

    mcx = BonsaiVariable("mcx", Regular(100, -8000.0, 8000.0), lambda x: x.mcx)
    mcy = BonsaiVariable("mcy", Regular(100, -8000.0, 8000.0), lambda x: x.mcy)
    mcz = BonsaiVariable("mcz", Regular(100, -8000.0, 8000.0), lambda x: x.mcz)
    mct = BonsaiVariable(
        "mct", Regular(100, -200.0, 0.0), lambda x: x.mct * 1e-3
    )  # TODO: understand units?

    deltax = BonsaiVariable(
        "deltax", Regular(100, -2000.0, 2000.0), lambda x: x.x - x.mcx
    )
    deltay = BonsaiVariable(
        "deltay", Regular(100, -2000.0, 2000.0), lambda x: x.y - x.mcy
    )
    deltaz = BonsaiVariable(
        "deltaz", Regular(100, -2000.0, 2000.0), lambda x: x.z - x.mcz
    )
    deltar = BonsaiVariable(
        "deltar",
        Regular(100, -2000.0, 2000.0),
        lambda x: np.sqrt((x.x - x.mcx) ** 2 + (x.y - x.mcy) ** 2 + (x.z - x.mcz) ** 2),
    )


class AnalysisVariableDefs(Enum):
    totalcharge = AnalysisVariable(
        "totalcharge",
        Regular(100, 0.0, 100.0),
        _total_charge,
    )
