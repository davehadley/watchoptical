import os
from argparse import ArgumentParser, Namespace

import matplotlib.pyplot as plt

from watchoptical.internal import timeconstants
from watchoptical.internal.client import ClientType, client
from watchoptical.internal.histoutils import categoryhistplot
from watchoptical.internal.opticsanalysis.runopticsanalysis import shelvedopticsanalysis, OpticsAnalysisResult
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
    _plothist(data)


def _xlabel(key: str) -> str:
    try:
        return {
            "n9_0" : "num PMT hits in 9 ns",
            "n9_1": "num PMT hits in 9 ns",
                }[key]
    except KeyError:
        return key


def _plothist(data: OpticsAnalysisResult, dest="plots"):
    for k, h in data.hist.items():
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax = categoryhistplot(h, lambda item: item.histogram * timeconstants.SECONDS_IN_WEEK, ax=ax)
        ax.set_ylabel("events per week")
        ax.set_yscale("log")
        ax.set_xlabel(_xlabel(k))
        ax.legend()
        fig.tight_layout()
        os.makedirs(dest, exist_ok=True)
        fig.savefig(f"{dest}{os.sep}{k}.png")
    return


def main():
    args = parsecml()
    dataset = WatchmanDataset(f for f in searchforrootfilesexcludinganalysisfiles(args.inputfiles)
                              if not ("IBDNeutron" in f or "IBDPosition" in f)
                              )
    with client(args.target):
        result = shelvedopticsanalysis(dataset, forcecall=args.force)
    plot(result)
    return


if __name__ == '__main__':
    main()
