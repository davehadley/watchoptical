from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np


@dataclass(frozen=True)
class Cut:
    apply: Callable[[np.ndarray], np.ndarray]
    name: Optional[str] = None

    def __call__(self, *args, **kwargs):
        return self.apply(*args, **kwargs)

    # def __eq__(self, other):
    #     return (self.name == other.name
    #             and
    #             self.apply.__code__.co_code == other.apply.__code__.co_code)
