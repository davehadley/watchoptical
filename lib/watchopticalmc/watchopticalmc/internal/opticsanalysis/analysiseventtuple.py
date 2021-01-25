import glob
import re
from typing import NamedTuple

import uproot
from cloudpickle import cloudpickle
from dask.bag import Bag
from pandas import DataFrame

from watchopticalmc.internal.opticsanalysis.analysisdataset import AnalysisDataset
from watchopticalmc.internal.generatemc.generatemc import GenerateMCConfig
from watchopticalmc.internal.generatemc.mctoanalysis import AnalysisFile, mctoanalysis
from watchopticalmc.internal.generatemc.runwatchmakerssensitivityanalysis import (
    WatchMakersSensitivityAnalysisConfig,
    WatchMakersSensitivityResult,
    runwatchmakerssensitivityanalysis,
)
from watchopticalmc.internal.generatemc.wmdataset import WatchmanDataset
import dask.bag


class AnalysisData(NamedTuple):
    pmt: DataFrame
    mc: DataFrame
    total: DataFrame

    @classmethod
    def fromAnalysisFile(cls, analysisfile: AnalysisFile) -> "AnalysisData":
        data = uproot.open(analysisfile.filename)["watchopticalanalysis"]
        dfs = [
            data.pandas.df([pattern], flatten=True)
            for pattern in ["pmt_*", "mc_*", "total_*"]
        ]
        return AnalysisData(*dfs)


class AnalysisEventTuple(NamedTuple):
    anal: AnalysisData
    bonsai: DataFrame
    analysisfile: AnalysisFile
    sensitivity: WatchMakersSensitivityResult
    generatemcconfig: GenerateMCConfig

    @property
    def numevents(self):
        return len(self.anal)

    @property
    def exposure(self):
        # exposure in seconds
        rate = _ratefromtree(self)
        return float(self.numevents) / rate

    @classmethod
    def load(cls, analysisfile: AnalysisFile) -> "AnalysisEventTuple":
        anal = AnalysisData.fromAnalysisFile(analysisfile)
        bonsai = (
            uproot.open(analysisfile.producedfrom.bonsaifile)["data"].pandas.df(
                flatten=False
            )
            # .set_index(["mcid", "subid"])
        )
        sensitivity = runwatchmakerssensitivityanalysis(
            WatchMakersSensitivityAnalysisConfig(
                analysisfile.producedfrom.rootdirectory
            )
        )
        generatemcconfig = _loadgeneratemcconfig(analysisfile)
        return AnalysisEventTuple(
            anal, bonsai, analysisfile, sensitivity, generatemcconfig
        )

    @classmethod
    def fromWatchmanDataset(cls, dataset: WatchmanDataset) -> Bag:
        return mctoanalysis(dataset).map(AnalysisEventTuple.load)

    @classmethod
    def fromAnalysisDataset(cls, dataset: AnalysisDataset) -> Bag:
        return dask.bag.from_sequence(dataset.analysisfiles).map(
            AnalysisEventTuple.load
        )

    @property
    def macro(self) -> str:
        return str(uproot.open(self.analysisfile.producedfrom.g4file)["macro"])


def _ratefromtree(tree: AnalysisEventTuple) -> float:
    # this should return the expect rate for this process in number of events per second
    lines = str(tree.macro).split("\n")
    for ln in lines:
        match = re.search("^/generator/rate/set (.*)", ln)
        if match:
            return float(match.group(1))
    raise ValueError("failed to parse macro", lines)


def _loadgeneratemcconfig(analysisfile: AnalysisFile) -> GenerateMCConfig:
    dirname = analysisfile.producedfrom.rootdirectory
    fname = glob.glob(f"{dirname}/watchopticalconfig_*.pickle")[0]
    with open(fname, "rb") as f:
        result = cloudpickle.load(f)
        assert isinstance(result, GenerateMCConfig)
        return result
