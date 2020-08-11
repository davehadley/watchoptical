import os
from argparse import ArgumentParser, Namespace

import matplotlib.pyplot as plt

from watchoptical.internal import timeconstants
from watchoptical.internal.client import ClientType, client
from watchoptical.internal.histoutils import categoryhistplot
from watchoptical.internal.runopticsanalysis import shelvedopticsanalysis, OpticsAnalysisResult
from watchoptical.internal.utils import searchforrootfilesexcludinganalysisfiles
from watchoptical.internal.wmdataset import WatchmanDataset


def parsecml() -> Namespace:
    parser = ArgumentParser(description="Process WATHCMAN MC files to the watchoptical analysis file format.")
    parser.add_argument("-d", "--directory", type=str, default=os.getcwd(),
                        help="Output Directory to store the generated files.")
    parser.add_argument("--target", "-t", type=ClientType, choices=list(ClientType),
                        default=ClientType.SINGLE,
                        help="Where to run jobs."
                        )
    parser.add_argument("inputfiles", nargs="+", type=str, default=[os.getcwd()])
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def plot(data: OpticsAnalysisResult):
    # categoryhistplot(hist["events_selected"], lambda item: item.histogram * timeconstants.SECONDS_IN_WEEK)
    categoryhistplot(data.hist["n9_1"], lambda item: item.histogram * timeconstants.SECONDS_IN_WEEK)
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
        result = shelvedopticsanalysis(dataset, forcecall=True)
    plot(result)
    return


if __name__ == '__main__':
    main()
