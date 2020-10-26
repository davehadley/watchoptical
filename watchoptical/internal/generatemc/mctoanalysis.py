import os
from dataclasses import dataclass
from typing import Optional

import dask
from dask.bag import Bag

from watchoptical.internal.generatemc.wmdataset import RatPacBonsaiPair, WatchmanDataset
from watchoptical.internal.watchopticalcpp import convert_ratpacbonsai_to_analysis


@dataclass(frozen=True)
class MCToAnalysisConfig:
    directory: str = os.getcwd()


@dataclass(frozen=True)
class AnalysisFile:
    filename: str
    producedfrom: RatPacBonsaiPair


def _outputfilename(files: RatPacBonsaiPair, config: MCToAnalysisConfig) -> str:
    return (
        f"{config.directory}"
        f"{os.sep}"
        f"watchopticalanalysis_"
        f"{os.path.basename(files.g4file)}"
    )


def _outputfileexists(files: RatPacBonsaiPair, config: MCToAnalysisConfig):
    return os.path.exists(_outputfilename(files, config))


def _run(files: RatPacBonsaiPair, config: MCToAnalysisConfig) -> AnalysisFile:
    outname = _outputfilename(files, config)
    if not os.path.exists(outname):
        convert_ratpacbonsai_to_analysis(files.g4file, files.bonsaifile, outname)
    return AnalysisFile(outname, files)


def mctoanalysis(
    dataset: WatchmanDataset, config: Optional[MCToAnalysisConfig] = None
) -> Bag:
    config = config if config is not None else MCToAnalysisConfig()
    return (
        dask.bag.from_sequence(dataset)
        # .filter(curry(complement(_outputfileexists))(config=config))
        .map(_run, config=config)
    )