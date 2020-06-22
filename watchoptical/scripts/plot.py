import functools
import operator
import os
import re
from argparse import ArgumentParser, Namespace
from typing import NamedTuple, Iterable

import uproot
import boost_histogram as bh

import matplotlib.pyplot as plt

from watchoptical.internal.client import ClientType, client
from watchoptical.internal.histoutils import CategoryHistogram, categoryhistplot, ExposureWeightedHistogram
from watchoptical.internal.mctoanalysis import mctoanalysis, AnalysisFile
from watchoptical.internal.wmdataset import WatchmanDataset


def parsecml() -> Namespace:
    parser = ArgumentParser(description="Process WATHCMAN MC files to the watchoptical analysis file format.")
    parser.add_argument("-d", "--directory", type=str, default=os.getcwd(),
                        help="Output Directory to store the generated files.")
    parser.add_argument("--target", "-t", type=ClientType, choices=list(ClientType),
                        default=ClientType.SINGLE,
                        help="Where to run jobs."
                        )
    parser.add_argument("--inputfiles", nargs="+", type=str, default=[
        "~/work/wm/data/testwatchoptical/attempt01/*_files_default/*/*.root"])
    return parser.parse_args()


class TreeTuple(NamedTuple):
    anal: dict
    bonsai: dict
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
    bonsai = uproot.open(analysisfile.producedfrom.bonsaifile)["data"].pandas.df(flatten=False)
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
        match = re.search("/generator/rate/set (.*)", l)
        if match:
            return float(match.group(1))
    raise ValueError("failed to parse macro", lines)


def categoryfromfile(file: AnalysisFile) -> str:
    et = eventtypefromfile(file)
    result = "IBD" if "IBD" in et else "Background"
    return result


def selection(data):
    # watchmakers efficiency is based on:
    #             cond = "closestPMT/1000.>%f"%(_d)
    #             cond += "&& good_pos>%f " %(_posGood)
    #             cond += "&& inner_hit > 4 &&  veto_hit < 4"
    #             cond += "&& n9 > %f" %(_n9)
    # with _distance2pmt=1,_n9=8,_dist=30.0,\
    # _posGood=0.1,_dirGood=0.1,_pe=8,_nhit=8,_itr = 1.5
    return data[(data.closestPMT/1000.0 > 4.0)
                & (data.good_pos > 0.1)
                & (data.inner_hit > 4)
                & (data.veto_hit < 4)
                ]


def analysis(tree: TreeTuple) -> bh.Histogram:
    histo = ExposureWeightedHistogram(bh.axis.Regular(100, 0.0, 60.0))
    category = categoryfromfile(tree.analysisfile)
    #histo.fill(category, tree.exposure, tree.bonsai["n9"])
    histo.fill(category, tree.exposure, selection(tree.bonsai).n9.array)
    return histo


def sumhistograms(iterable: Iterable[bh.Histogram]) -> bh.Histogram:
    return functools.reduce(operator.add, iterable)


def plot(dataset: WatchmanDataset):
    analfiles = mctoanalysis(dataset)
    data = (analfiles.map(load)
            .map(analysis)
            .reduction(sumhistograms, sumhistograms)
            ).compute()
    categoryhistplot(data)
    plt.yscale("log")
    plt.legend()
    plt.show()
    return


def main():
    args = parsecml()
    dataset = WatchmanDataset(args.inputfiles)
    with client(args.target):
        plot(dataset)
    return


if __name__ == '__main__':
    main()
