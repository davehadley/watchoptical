from enum import Enum
from typing import Any, Callable, NamedTuple

import numpy as np
from boost_histogram.axis import Axis, Regular
from pandas import DataFrame


class Variable(NamedTuple):
    name: str
    binning: Axis
    f: Callable[[DataFrame], Any]

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)


class VariableDefs(Enum):
    eventcount = Variable(
        "eventcount", Regular(1, 0.0, 1.0), lambda x: np.zeros(len(x))
    )
    n9 = Variable("n9", Regular(26, 0.0, 60.0), lambda x: x.n9)
    innerPE = Variable("innerPE", Regular(100, 0.0, 100.0), lambda x: x.innerPE)
    mcenergy = Variable("mcenergy", Regular(100, 0.0, 10.0), lambda x: x.mc_energy)
    innerPE_over_mcenergy = Variable(
        "innerPE_over_mcenergy",
        Regular(100, 0.0, 50.0),
        lambda x: x.innerPE / x.mc_energy,
    )

    recox = Variable("recox", Regular(100, -8000.0, 8000.0), lambda x: x.x)
    recoy = Variable("recoy", Regular(100, -8000.0, 8000.0), lambda x: x.y)
    recoz = Variable("recoz", Regular(100, -8000.0, 8000.0), lambda x: x.z)
    recot = Variable("recot", Regular(100, -100.0, 10.0), lambda x: x.t)

    mcx = Variable("mcx", Regular(100, -8000.0, 8000.0), lambda x: x.mcx)
    mcy = Variable("mcy", Regular(100, -8000.0, 8000.0), lambda x: x.mcy)
    mcz = Variable("mcz", Regular(100, -8000.0, 8000.0), lambda x: x.mcz)
    mct = Variable(
        "mct", Regular(100, -200.0, 0.0), lambda x: x.mct * 1e-3
    )  # TODO: understand units?

    deltax = Variable("deltax", Regular(100, -2000.0, 2000.0), lambda x: x.x - x.mcx)
    deltay = Variable("deltay", Regular(100, -2000.0, 2000.0), lambda x: x.y - x.mcy)
    deltaz = Variable("deltaz", Regular(100, -2000.0, 2000.0), lambda x: x.z - x.mcz)
    deltar = Variable(
        "deltar",
        Regular(100, -2000.0, 2000.0),
        lambda x: np.sqrt((x.x - x.mcx) ** 2 + (x.y - x.mcy) ** 2 + (x.z - x.mcz) ** 2),
    )
