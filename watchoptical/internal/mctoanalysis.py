import os
import tempfile
from dataclasses import dataclass, field
from typing import Optional

import dask
from dask.bag import Bag

from watchoptical.internal.wmdataset import WatchmanDataset, RatPacBonsaiPair
from watchoptical.internal.watchopticalcpp import convert_ratpacbonsai_to_analysis

@dataclass(frozen=True)
class MCToAnalysisConfig:
    directory: str = os.getcwd()


def _outputfilename(files :RatPacBonsaiPair, config: MCToAnalysisConfig) -> str:
    return f"{config.directory}{os.sep}watchopticalanalysis_{os.path.basename(files.g4file)}"

def _run(files :RatPacBonsaiPair, config: MCToAnalysisConfig) -> str:
    outname = _outputfilename(files, config)
    convert_ratpacbonsai_to_analysis(files.g4file, files.bonsaifile, outname)
    return outname

def mctoanalysis(dataset: WatchmanDataset, config: Optional[MCToAnalysisConfig]=None) -> Bag:
    config = config if config is not None else MCToAnalysisConfig()
    return (dask.bag.from_sequence(dataset)
            .map(_run, config=config)
            )
