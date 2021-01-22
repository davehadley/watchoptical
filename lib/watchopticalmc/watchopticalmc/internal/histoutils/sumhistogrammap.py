from typing import Dict, Iterable

import boost_histogram as bh

from watchopticalmc.internal.utils.collectionutils import summap


def sumhistogrammap(
    iterable: Iterable[Dict[str, bh.Histogram]]
) -> Dict[str, bh.Histogram]:
    return summap(iterable)
