import re
from dataclasses import dataclass, field
from typing import Iterable, Mapping, Callable, Any, Optional, MutableMapping

import boost_histogram as bh
import numpy as np
import uproot
from dask.bag import Bag
from pandas import DataFrame
from toolz import identity

from watchoptical.internal.analysiseventtuple import AnalysisEventTuple
from watchoptical.internal.eventtype import eventtypefromfile
from watchoptical.internal.histoutils import ExposureWeightedHistogram, sumhistogrammap
from watchoptical.internal.mctoanalysis import AnalysisFile, mctoanalysis
from watchoptical.internal.utils import summap, shelveddecorator, sumlist
from watchoptical.internal.wmdataset import WatchmanDataset


@dataclass
class OpticsAnalysisResult:
    hist: MutableMapping[str, ExposureWeightedHistogram] = field(default_factory=dict)
    scatter: dict = field(default_factory=dict)

    def __add__(self, other):
        return OpticsAnalysisResult(
            hist=summap([self.hist, other.hist]),
            scatter=summap([self.scatter, other.scatter]),
        )


def _categoryfromfile(file: AnalysisFile) -> str:
    et = eventtypefromfile(file)
    result = "IBD" if "IBD" in et else "Background"
    return result


def _hascoincidence(data):
    t = data.groupby("mcid").t
    count = t.transform("count")
    dt = t.transform(lambda t: t.max() - t.min())
    return (count >= 2) & (dt.abs() < 50.0)


def _selection(data):
    # watchmakers efficiency is based on:
    #             cond = "closestPMT/1000.>%f"%(_d)
    #             cond += "&& good_pos>%f " %(_posGood)
    #             cond += "&& inner_hit > 4 &&  veto_hit < 4"
    #             cond += "&& n9 > %f" %(_n9)
    # with _distance2pmt=1,_n9=8,_dist=30.0,\
    # _posGood=0.1,_dirGood=0.1,_pe=8,_nhit=8,_itr = 1.5
    return data[((data.closestPMT / 1500.0) > 1.0)
                & (data.good_pos > 0.1)
                & (data.inner_hit > 4)
                & (data.veto_hit < 4)
                & _hascoincidence(data)
                ]


def _makebonsaihistogram(tree: AnalysisEventTuple,
                         binning: bh.axis.Axis,
                         x: Callable[[DataFrame], Any],
                         w: Optional[Callable[[DataFrame], Any]] = None,
                         selection: Callable[[DataFrame], DataFrame] = _selection,
                         subevent: int = 0
                         ) -> ExposureWeightedHistogram:
    histo = ExposureWeightedHistogram(binning)
    category = _categoryfromfile(tree.analysisfile)
    data = (selection(tree.bonsai)
            .groupby("mcid")
            .nth(subevent))
    xv = np.asarray(x(data))
    wv = None if not w else np.asarray(w(data))
    histo.fill(category, tree.exposure, xv, weight=wv)
    return histo


def _makebasichistograms(tree: AnalysisEventTuple, hist: MutableMapping[str, ExposureWeightedHistogram]):
    hist["events_withatleastonesubevent"] = _makebonsaihistogram(tree, bh.axis.Regular(1, 0.0, 1.0),
                                                                 lambda x: np.zeros(len(x)), selection=identity)
    hist["events_selected"] = _makebonsaihistogram(tree, bh.axis.Regular(1, 0.0, 1.0),
                                                   lambda x: np.zeros(len(x)), selection=_selection)
    hist["n9_0"] = _makebonsaihistogram(tree, bh.axis.Regular(26, 0., 60.0),
                                        lambda x: x.n9)
    hist["n9_1"] = _makebonsaihistogram(tree, bh.axis.Regular(26, 0., 60.0),
                                        lambda x: x.n9,
                                        subevent=1)
    return


def _attenuationfromtree(tree: AnalysisEventTuple) -> float:
    # this should return the expect rate for this process in number of events per second
    lines = str(tree.macro).split("\n")
    for l in lines:
        match = re.search("^/rat/db/set OPTICS\[water\] ABSLENGTH_value2 (.*?) ", l)
        if match:
            return float(match.group(1))
    raise ValueError("failed to parse macro", lines)


def _makebasicattenuationscatter(tree: AnalysisEventTuple, store: dict):
    category = _categoryfromfile(tree.analysisfile)
    if category == "IBD":
        attenuation = _attenuationfromtree(tree)
        store["ibd_total_charge_by_attenuation"] = (ExposureWeightedHistogram(bh.axis.Regular(300, 0.0, 150.0))
                                     .fill(f"{attenuation:0.5e}", tree.exposure, tree.anal.pmt_q.groupby("entry").sum().array)
                                     )
    return


def _analysis(tree: AnalysisEventTuple) -> OpticsAnalysisResult:
    # histo.fill(category, tree.exposure, tree.bonsai.n9.array)
    result = OpticsAnalysisResult()
    _makebasichistograms(tree, result.hist)
    _makebasicattenuationscatter(tree, result.hist)
    return result


def runopticsanalysis(dataset: WatchmanDataset) -> Bag:
    analfiles = mctoanalysis(dataset)
    hist = (analfiles.map(AnalysisEventTuple.load)
            .map(_analysis)
            .reduction(sumlist, sumlist)
            )
    return hist


@shelveddecorator(lambda d: f"opticsanalysis/{d.name}")
def shelvedopticsanalysis(dataset: WatchmanDataset) -> OpticsAnalysisResult:
    return runopticsanalysis(dataset).compute()
