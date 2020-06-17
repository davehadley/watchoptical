import os
from argparse import ArgumentParser, Namespace
from typing import NamedTuple, Any

from IPython import embed

import uproot
from uproot.write.objects import TTree

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
        "~/work/wm/data/testwatchoptical/attempt01/*_files_default/*IBD_LIQUID_pn_ibd*/*.root"])
    return parser.parse_args()

class TreeTuple(NamedTuple):
    anal: dict
    bonsai: dict

def load(analysisfile: AnalysisFile):
    anal = uproot.open(analysisfile.filename)["watchopticalanalysis"].arrays()
    bonsai = uproot.open(analysisfile.producedfrom.bonsaifile)["data"].arrays()
    return TreeTuple(anal, bonsai)


def plot(dataset: WatchmanDataset):
    analfiles = mctoanalysis(dataset)
    data = analfiles.map(load).compute()
    #embed()
    #plt.hist(data[0].anal[b"total_charge"], label="q")
    plt.hist(data[0].bonsai[b"n9"], label="n9")
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
