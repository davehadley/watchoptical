from enum import Enum
from typing import NamedTuple, Callable, Any

from pandas import DataFrame

import numpy as np

class Variable(NamedTuple):
    name: str
    f: Callable[[DataFrame], Any]

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)


class VariableDefs(Enum):
    eventcount = Variable("eventcount", lambda x: np.zeros(len(x)))
    n9 = Variable("n9", lambda x: np.zeros(len(x)))