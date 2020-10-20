from typing import Callable, NamedTuple, Optional

import numpy as np


class Cut(NamedTuple):
    apply: Callable[[np.ndarray], np.ndarray]
    name: Optional[str] = None

    def __call__(self, *args, **kwargs):
        return self.apply(*args, **kwargs)
