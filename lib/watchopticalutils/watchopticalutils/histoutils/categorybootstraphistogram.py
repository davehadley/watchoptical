from copy import deepcopy
from typing import Any, Collection, Dict, Iterator, NamedTuple, Optional, Union

import bootstraphistogram
import numpy as np


class CategoryBootstrapHistogram(Collection):
    Category = Union[Any]

    class Item(NamedTuple):
        category: "CategoryBootstrapHistogram.Category"
        histogram: bootstraphistogram.BootstrapHistogram

    def __init__(
        self, *axes: bootstraphistogram.axis.Axis, numsamples=10, **kwargs: Any
    ):
        self._args = axes
        self._kwargs = dict(kwargs)
        self._kwargs["numsamples"] = numsamples
        self._hist: Dict[
            "CategoryBootstrapHistogram.Category",
            bootstraphistogram.BootstrapHistogram,
        ] = dict()

    def fill(
        self,
        category: "CategoryBootstrapHistogram.Category",
        *args: Union[float, np.ndarray],
        weight: Optional[Union[float, np.ndarray]] = None,
    ) -> "CategoryBootstrapHistogram":
        if category not in self._hist:
            self._hist[category] = bootstraphistogram.BootstrapHistogram(
                *self._args, **self._kwargs
            )
        self._hist[category].fill(*args, weight=weight)
        return self

    def __iter__(self) -> Iterator[Item]:
        for index, hist in sorted(self._hist.items()):
            yield self.Item(index, hist)

    def __len__(self) -> int:
        return len(self._hist)

    def __contains__(self, __x: object) -> bool:
        return __x in self._hist

    def __add__(self, other) -> "CategoryBootstrapHistogram":
        result = deepcopy(self)
        for key, value in other._hist.items():
            try:
                result._hist[key] += value
            except KeyError:
                result._hist[key] = deepcopy(value)
        return result
