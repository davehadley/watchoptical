from typing import Callable, NamedTuple, Optional

from pandas import DataFrame, Series


class Cut(NamedTuple):
    apply: Callable[[DataFrame], Series]
    name: Optional[str] = None

    def __call__(self, *args, **kwargs):
        return self.apply(*args, **kwargs)
