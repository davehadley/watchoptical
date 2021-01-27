from enum import Enum

from watchopticalanalysis.algs.resolution import Resolution

# from watchopticalanalysis.algs.basichist import BasicHist
from watchopticalanalysis.algs.selectiontables import SelectionTables

from .timestamp import Timestamp


class AlgDefs(Enum):
    timestamp = Timestamp
    selectiontables = SelectionTables
    resolution = Resolution
    # basichist = BasicHist
