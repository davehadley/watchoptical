import os
from argparse import ArgumentParser, Namespace

import matplotlib.pyplot as plt
import numpy as np

from watchoptical.internal import timeconstants
from watchoptical.internal.client import ClientType, client
from watchoptical.internal.histoutils import categoryhistplot
from watchoptical.internal.opticsanalysis.runopticsanalysis import shelvedopticsanalysis, OpticsAnalysisResult
from watchoptical.internal.utils import searchforrootfilesexcludinganalysisfiles
from watchoptical.internal.wmdataset import WatchmanDataset


def parsecml() -> Namespace:
    parser = ArgumentParser(description="Process WATCHMAN MC files to the watchoptical analysis file format.")
    parser.add_argument("-d", "--directory", type=str, default=os.getcwd(),
                        help="Output Directory to store the generated files.")
    parser.add_argument("--target", "-t", type=ClientType, choices=list(ClientType),
                        default=ClientType.SINGLE,
                        help="Where to run jobs."
                        )
    parser.add_argument("inputfiles", nargs="+", type=str, default=[os.getcwd()])
    parser.add_argument("--force", "-f", action="store_true")
    return parser.parse_args()


def plot(data: OpticsAnalysisResult):
    _plothist(data)
    _plotattenuation(data)
    return


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
        #ax.set_yscale("log")
        ax.set_xlabel(_xlabel(k))
        ax.legend()
        fig.tight_layout()
        fig.tight_layout()
        os.makedirs(dest, exist_ok=True)
        fig.savefig(f"{dest}{os.sep}{k}.png")
    return


def _plotattenuation(data: OpticsAnalysisResult, dest="plots"):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for key, label in [("idb_total_charge_by_attenuation_mean", "mean"),
                       ("idb_total_charge_by_attenuation_mean_gt10", "mean | Q > 10"),
                       ]:
        points = data.scatter[key]
        points = [(float(a)/1.0e3, q.value, np.sqrt(q.variance)/np.sqrt(q.sum_of_weights)) for a, q in points.items()]
        X, Y, Yerr = zip(*points)
        ax.errorbar(list(X), list(Y), yerr=Yerr, ls="", marker="o", label=label)
    ax.legend()
    os.makedirs(dest, exist_ok=True)
    ax.set_ylabel("total charge per event")
    ax.set_xscale("log")
    ax.set_xlabel("attenuation length [m]")
    fig.tight_layout()
    fig.savefig(f"{dest}{os.sep}attenuationmean.png")
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
