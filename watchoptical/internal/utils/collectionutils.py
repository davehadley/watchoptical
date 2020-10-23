import functools
import operator
from typing import Any, Callable, Dict, Iterable

from toolz import merge_with


def sumlist(iterable: Iterable[Any]):
    return functools.reduce(operator.add, iterable)


def summap(
    iterable: Iterable[Dict[Any, Any]], add: Callable = operator.add
) -> Dict[Any, Any]:
    sum = functools.partial(functools.reduce, add)
    return functools.reduce(functools.partial(merge_with, sum), iterable)
