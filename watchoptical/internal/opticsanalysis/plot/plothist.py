import os

import matplotlib.pyplot as plt

from watchoptical.internal import timeconstants
from watchoptical.internal.histoutils import categoryhistplot
from watchoptical.internal.opticsanalysis.runopticsanalysis import OpticsAnalysisResult


def plothist(data: OpticsAnalysisResult, dest: str = "plots") -> None:
    _plothist(data, dest)


def _xlabel(key: str) -> str:
    try:
        return {
            "n9_0": "num PMT hits in 9 ns",
            "n9_1": "num PMT hits in 9 ns",
        }[key]
    except KeyError:
        return key


def _plothist(data: OpticsAnalysisResult, dest="plots"):
    for k, h in data.hist.items():
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax = categoryhistplot(
            h, lambda item: item.histogram * timeconstants.SECONDS_IN_WEEK, ax=ax
        )
        ax.set_ylabel("events per week")
        # ax.set_yscale("log")
        ax.set_xlabel(_xlabel(k))
        ax.legend()
        fig.tight_layout()
        fig.tight_layout()
        os.makedirs(dest, exist_ok=True)
        fig.savefig(f"{dest}{os.sep}{k}.png")
    return
