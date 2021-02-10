from typing import Dict, Iterable

import boost_histogram as bh

from watchopticalutils.collectionutils import summap


def sumhistogrammap(
    iterable: Iterable[Dict[str, bh.Histogram]]
) -> Dict[str, bh.Histogram]:
    return summap(iterable)
