from pathlib import Path
from typing import List, NamedTuple

import cloudpickle
from watchopticalmc.internal.generatemc.mctoanalysis import AnalysisFile
from watchopticalmc.internal.generatemc.wmdataset import WatchmanDataset

_DEFAULT_FILE_NAME = "analysisdataset.pickle"


class AnalysisDataset(NamedTuple):
    inputfiles: List[Path]
    directory: Path
    sourcedataset: WatchmanDataset
    analysisfiles: List[AnalysisFile]

    @classmethod
    def load(cls, path: Path) -> "AnalysisDataset":
        if path.is_dir():
            path = path / _DEFAULT_FILE_NAME
        with open(path, "rb") as fp:
            return cloudpickle.load(fp)

    def write(self, path: Path) -> None:
        if path.is_dir():
            path = path / _DEFAULT_FILE_NAME
        with open(path, "wb") as fp:
            cloudpickle.dump(self, fp)
