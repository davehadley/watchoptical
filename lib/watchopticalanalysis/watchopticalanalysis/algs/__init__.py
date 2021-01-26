from enum import Enum

from watchopticalanalysis.algs.basichist import BasicHist
from watchopticalanalysis.algs.selectiontables import SelectionTables

from .test import Test


class AlgDefs(Enum):
    test = Test
    selectiontables = SelectionTables
    basichist = BasicHist
