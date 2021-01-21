import os

from matplotlib.figure import Figure

from watchoptical.internal.histoutils import categoryhistplot
from watchoptical.internal.opticsanalysis.runopticsanalysis import OpticsAnalysisResult
from watchoptical.internal.utils import timeconstants


def plothist(data: OpticsAnalysisResult, dest: str = "plots") -> None:
    _plothist(data, dest=f"{dest}{os.sep}hist")


def _xlabel(key: str) -> str:
    try:
        return {
            "n9_0": "num PMT hits in 9 ns",
            "n9_1": "num PMT hits in 9 ns",
        }[key]
    except KeyError:
        return key


def _plothist(data: OpticsAnalysisResult, dest):
    for key, h in data.hist.items():
        for yscale in ("linear", "log"):
            fig = Figure()
            ax = fig.add_subplot(111)
            ax = categoryhistplot(
                h,  # type: ignore
                lambda item: item.histogram * timeconstants.SECONDS_IN_WEEK,
                formatlabel=lambda item: f"{item.category.eventtype} "
                f"{item.category.attenuation}",
                ax=ax,
            )
            ax.set_ylabel("events per week")
            ax.set_yscale(yscale)
            ax.set_xlabel(_xlabel(key))
            ax.legend()
            fig.tight_layout()
            fname = f"{dest}{os.sep}{key}_{yscale}.png"
            os.makedirs(os.path.dirname(fname), exist_ok=True)
            fig.savefig(fname)
    return
