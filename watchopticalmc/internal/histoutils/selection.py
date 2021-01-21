import operator
from functools import reduce
from typing import NamedTuple, Tuple

import numpy as np

from watchopticalmc.internal.histoutils.cut import Cut


class Selection(NamedTuple):
    name: str
    cuts: Tuple[Cut, ...]

    def apply(self, data: np.ndarray) -> np.ndarray:
        selected = reduce(operator.and_, (c(data) for c in self.cuts))
        return data[selected]

    def __call__(self, *args, **kwargs):
        return self.apply(*args, **kwargs)
