import functools
import operator
import os
from argparse import ArgumentParser, Namespace
from typing import NamedTuple, Any, Iterable

from IPython import embed

import uproot
from uproot.write.objects import TTree
import boost_histogram as bh
import mplhep as hep

import numpy as np
import matplotlib.pyplot as plt

from watchoptical.internal.client import ClientType, client
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

def load(analysisfile: AnalysisFile) -> TreeTuple:
    anal = uproot.open(analysisfile.filename)["watchopticalanalysis"].lazyarrays()
    bonsai = uproot.open(analysisfile.producedfrom.bonsaifile)["data"].lazyarrays()
    return TreeTuple(anal, bonsai)

def analysis(tree: TreeTuple) -> bh.Histogram:
    histo = bh.Histogram(bh.axis.Regular(100, 0.0, 60.0))
    histo.fill(tree.bonsai["n9"])
    return histo

def sumhistograms(iterable: Iterable[bh.Histogram]) -> bh.Histogram:
    return functools.reduce(operator.add, iterable)

def plot(dataset: WatchmanDataset):
    analfiles = mctoanalysis(dataset)
    data = (analfiles.map(load)
            .map(analysis)
            .reduction(sumhistograms, sumhistograms)
            ).compute()
    #embed()
    #plt.hist(data[0].anal[b"total_charge"], label="q")
    hep.histplot(data)
    plt.legend()
    plt.show()
    input("wait")
    return


def main():
    args = parsecml()
    dataset = WatchmanDataset(args.inputfiles)
    with client(args.target):
        plot(dataset)
    return


if __name__ == '__main__':
    main()
