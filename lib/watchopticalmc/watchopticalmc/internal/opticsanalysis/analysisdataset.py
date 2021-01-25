from watchopticalmc.internal.generatemc.mctoanalysis import AnalysisFile
from watchopticalmc.internal.generatemc.wmdataset import WatchmanDataset, RatPacBonsaiPair
from pathlib import Path
from typing import List
from typing import NamedTuple
import cloudpickle

class AnalysisDataset(NamedTuple):
    inputfiles: List[Path]
    directory: Path
    sourcedataset: WatchmanDataset
    analysisfiles: List[AnalysisFile]

    @classmethod
    def load(cls, path :Path) -> "AnalysisDataset":
        with open(path, "rb") as fp:
            return cloudpickle.load(fp)

    def write(self, path :Path) -> None:
        with open(path, "wb") as fp:
            cloudpickle.dump(self, fp)
