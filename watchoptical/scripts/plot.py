import functools
import operator
import os
import re
import shelve
from argparse import ArgumentParser, Namespace
from typing import NamedTuple, Iterable, Mapping, Callable, Any, Optional

import uproot
import boost_histogram as bh
import numpy as np

import matplotlib.pyplot as plt
from pandas import DataFrame, Series
from toolz import merge_with, first, identity

from watchoptical.internal import timeconstants
from watchoptical.internal.client import ClientType, client
from watchoptical.internal.histoutils import CategoryHistogram, categoryhistplot, ExposureWeightedHistogram
from watchoptical.internal.mctoanalysis import mctoanalysis, AnalysisFile
from watchoptical.internal.utils import findfiles, searchdirectories, searchforrootfilesexcludinganalysisfiles
from watchoptical.internal.wmdataset import WatchmanDataset

AnalysisResult = Mapping[str, bh.Histogram]


def parsecml() -> Namespace:
    parser = ArgumentParser(description="Process WATHCMAN MC files to the watchoptical analysis file format.")
    parser.add_argument("-d", "--directory", type=str, default=os.getcwd(),
                        help="Output Directory to store the generated files.")
    parser.add_argument("--target", "-t", type=ClientType, choices=list(ClientType),
                        default=ClientType.SINGLE,
                        help="Where to run jobs."
                        )
    parser.add_argument("inputfiles", nargs="+", type=str, default=[os.getcwd()])
    parser.add_argument("force", action="store_true")
    return parser.parse_args()


class TreeTuple(NamedTuple):
    anal: DataFrame
    bonsai: DataFrame
    analysisfile: AnalysisFile

    @property
    def numevents(self):
        return len(self.anal)

    @property
    def exposure(self):
        # exposure in seconds
        rate = ratefromtree(self)
        return float(self.numevents) / rate


def load(analysisfile: AnalysisFile) -> TreeTuple:
    anal = uproot.open(analysisfile.filename)["watchopticalanalysis"].pandas.df(flatten=False)
    bonsai = (uproot.open(analysisfile.producedfrom.bonsaifile)["data"]
              .pandas.df(flatten=False)
              # .set_index(["mcid", "subid"])
              )
    return TreeTuple(anal, bonsai, analysisfile)


def eventtypefromfile(file: AnalysisFile) -> str:
    fname = file.producedfrom.g4file
    try:
        result = re.match(".*/Watchman_(.*)/.*", fname).group(1)
    except AttributeError:
        result = "unknown"
    return result


def ratefromtree(tree: TreeTuple) -> float:
    # this should return the expect rate for this process in number of events per second
    lines = str(uproot.open(tree.analysisfile.producedfrom.g4file)["macro"]).split("\n")
    for l in lines:
        match = re.search("^/generator/rate/set (.*)", l)
        if match:
            return float(match.group(1))
    raise ValueError("failed to parse macro", lines)


def categoryfromfile(file: AnalysisFile) -> str:
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


def _makebonsaihistogram(tree: TreeTuple,
                         binning: bh.axis.Axis,
                         x: Callable[[DataFrame], Any],
                         w: Optional[Callable[[DataFrame], Any]] = None,
                         selection: Callable[[DataFrame], DataFrame] = selection,
                         subevent: int = 0
                         ) -> ExposureWeightedHistogram:
    histo = ExposureWeightedHistogram(binning)
    category = categoryfromfile(tree.analysisfile)
    data = (selection(tree.bonsai)
            .groupby("mcid")
            .nth(subevent))
    xv = np.asarray(x(data))
    wv = None if not w else np.asarray(w(data))
    histo.fill(category, tree.exposure, xv, weight=wv)
    return histo


def analysis(tree: TreeTuple) -> AnalysisResult:
    category = categoryfromfile(tree.analysisfile)
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


def sumhistograms(iterable: Iterable[Mapping[str, bh.Histogram]]) -> Mapping[str, bh.Histogram]:
    sum = functools.partial(functools.reduce, operator.add)
    return functools.reduce(functools.partial(merge_with, sum), iterable)


def getorcompute(key: str, f: Callable, dbname: str="watchoptical.shelve.db", forcecompute: bool=False):
    with shelve.open(dbname) as db:
        if key in db and not forcecompute:
            return db[key]
        else:
            result = f()
            db[key] = result
            return result


def runanalysis(dataset: WatchmanDataset) -> AnalysisResult:
    analfiles = mctoanalysis(dataset)
    hist = (analfiles.map(load)
            .map(analysis)
            .reduction(sumhistograms, sumhistograms)
            )
    return hist


def plot(data: AnalysisResult):
    # categoryhistplot(hist["events_selected"], lambda item: item.histogram * timeconstants.SECONDS_IN_WEEK)
    categoryhistplot(data["n9_1"], lambda item: item.histogram * timeconstants.SECONDS_IN_WEEK)
    # categoryhistplot()
    plt.ylabel("events per week")
    plt.yscale("log")
    plt.xlabel("num PMT hits in 9 ns (n9)")
    plt.legend()
    plt.savefig("n9.png")
    plt.show()
    return


def main():
    args = parsecml()
    dataset = WatchmanDataset(f for f in searchforrootfilesexcludinganalysisfiles(args.inputfiles)
                              if not ("IBDNeutron" in f or "IBDPosition" in f)
                              )
    with client(args.target):
        result = getorcompute(f"analysis/{dataset.name}", runanalysis(dataset).compute, forcecompute=args.force)
    plot(result)
    return


if __name__ == '__main__':
    main()
