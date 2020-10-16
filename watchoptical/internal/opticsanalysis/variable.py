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
