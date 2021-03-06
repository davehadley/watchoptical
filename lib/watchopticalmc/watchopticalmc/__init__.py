from watchopticalmc import _version
from watchopticalmc.internal.generatemc.mctoanalysis import AnalysisFile
from watchopticalmc.internal.generatemc.wmdataset import (
    RatPacBonsaiPair,
    WatchmanDataset,
)
from watchopticalmc.internal.opticsanalysis.analysisdataset import AnalysisDataset
from watchopticalmc.internal.opticsanalysis.analysiseventtuple import AnalysisEventTuple

__version__ = _version.__version__
__license__ = "MIT"
__author__ = "David Hadley"
url = "https://github.com/davehadley/watchoptical"

__all__ = [
    "AnalysisFile",
    "AnalysisEventTuple",
    "AnalysisDataset",
    "WatchmanDataset",
    "RatPacBonsaiPair",
]
