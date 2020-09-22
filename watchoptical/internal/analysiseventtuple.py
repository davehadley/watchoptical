import re
from typing import NamedTuple

from pandas import DataFrame

import uproot
from watchoptical.internal.mctoanalysis import AnalysisFile


class AnalysisEventTuple(NamedTuple):
    anal: DataFrame
    bonsai: DataFrame
    analysisfile: AnalysisFile

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
        anal = uproot.open(analysisfile.filename)["watchopticalanalysis"].pandas.df(["pmt_*"])
        bonsai = (uproot.open(analysisfile.producedfrom.bonsaifile)["data"]
                  .pandas.df(flatten=False)
                  # .set_index(["mcid", "subid"])
                  )
        return AnalysisEventTuple(anal, bonsai, analysisfile)

    @property
    def macro(self) -> str:
        return str(uproot.open(self.analysisfile.producedfrom.g4file)["macro"])


def _ratefromtree(tree: AnalysisEventTuple) -> float:
    # this should return the expect rate for this process in number of events per second
    lines = str(tree.macro).split("\n")
    for l in lines:
        match = re.search("^/generator/rate/set (.*)", l)
        if match:
            return float(match.group(1))
    raise ValueError("failed to parse macro", lines)
