from enum import Enum

from watchopticalanalysis.algs.selectiontables import SelectionTables

from .test import Test


class AlgDefs(Enum):
    test = Test
    selectiontables = SelectionTables
    # hist = partial(plothist)
    # scatter = partial(plotscatter)
    # attenuation = partial(plotattenuation)
    # dumpselectionstats = partial(dumpselectiontables)
