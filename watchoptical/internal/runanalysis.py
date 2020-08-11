from typing import Iterable, Mapping, Callable, Any, Optional

import boost_histogram as bh
import numpy as np
from dask.bag import Bag
from pandas import DataFrame
from toolz import identity

from watchoptical.internal.analysiseventtuple import AnalysisEventTuple
from watchoptical.internal.eventtype import eventtypefromfile
from watchoptical.internal.histoutils import ExposureWeightedHistogram, sumhistogrammap
from watchoptical.internal.mctoanalysis import AnalysisFile, mctoanalysis
from watchoptical.internal.utils import summap, shelveddecorator
from watchoptical.internal.wmdataset import WatchmanDataset

AnalysisResult = Mapping[str, ExposureWeightedHistogram]


def _categoryfromfile(file: AnalysisFile) -> str:
    et = eventtypefromfile(file)
    result = "IBD" if "IBD" in et else "Background"
    return result


def _hascoincidence(data):
    t = data.groupby("mcid").t
    count = t.transform("count")
    dt = t.transform(lambda t: t.max() - t.min())
    return (count >= 2) & (dt.abs() < 50.0)


def selection(data):
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
                         selection: Callable[[DataFrame], DataFrame] = selection,
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


def analysis(tree: AnalysisEventTuple) -> AnalysisResult:
    # histo.fill(category, tree.exposure, tree.bonsai.n9.array)
    result = {}
    result["events_withatleastonesubevent"] = _makebonsaihistogram(tree, bh.axis.Regular(1, 0.0, 1.0),
                                                                   lambda x: np.zeros(len(x)), selection=identity)
    result["events_selected"] = _makebonsaihistogram(tree, bh.axis.Regular(1, 0.0, 1.0),
                                                     lambda x: np.zeros(len(x)), selection=selection)
    result["n9_0"] = _makebonsaihistogram(tree, bh.axis.Regular(26, 0., 60.0),
                                          lambda x: x.n9)
    result["n9_1"] = _makebonsaihistogram(tree, bh.axis.Regular(26, 0., 60.0),
                                          lambda x: x.n9,
                                          subevent=1)
    return result


def runanalysis(dataset: WatchmanDataset) -> Bag:
    analfiles = mctoanalysis(dataset)
    hist = (analfiles.map(AnalysisEventTuple.load)
            .map(analysis)
            .reduction(summap, summap)
            )
    return hist


@shelveddecorator(lambda d: f"analysis/{d.name}")
def shelvedanalysis(dataset: WatchmanDataset) -> AnalysisResult:
    return runanalysis(dataset).compute()