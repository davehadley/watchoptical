import os

import matplotlib.pyplot as plt
import numpy as np

from watchoptical.internal.opticsanalysis.runopticsanalysis import OpticsAnalysisResult


def plotattenuation(data: OpticsAnalysisResult, dest: str = "plots") -> None:
    _plotattenuation(data, dest)


def _plotattenuation(data: OpticsAnalysisResult, dest="plots"):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for key, label in [
        ("idb_total_charge_by_attenuation_mean", "mean"),
        # ("idb_total_charge_by_attenuation_mean_gt10", "mean | Q > 10"),
    ]:
        points = data.scatter[key]
        processedpoints = [
            (
                category.attenuation / 1.0e3,
                q.value,
                np.sqrt(q.variance) / np.sqrt(q.sum_of_weights),
            )
            for category, q in points
        ]
        X, Y, Yerr = zip(*processedpoints)
        ax.errorbar(list(X), list(Y), yerr=Yerr, ls="", marker="o", label=label)
    ax.legend()
    os.makedirs(dest, exist_ok=True)
    ax.set_ylabel("total charge per event")
    ax.set_xscale("log")
    ax.set_xlabel("attenuation length [m]")
    fig.tight_layout()
    fig.savefig(f"{dest}{os.sep}attenuationmean.png")
    return
