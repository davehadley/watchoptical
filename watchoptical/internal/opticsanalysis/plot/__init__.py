from enum import Enum
from functools import partial
from typing import Optional

from watchoptical.internal.opticsanalysis.plot.plotattenuation import plotattenuation
from watchoptical.internal.opticsanalysis.plot.plothist import plothist
from watchoptical.internal.opticsanalysis.runopticsanalysis import OpticsAnalysisResult


class PlotMode(Enum):
    hist = partial(plothist)
    attenuation = partial(plotattenuation)


def plot(data: OpticsAnalysisResult, dest: str, mode: Optional[PlotMode] = None):
    for p in [mode] if mode is not None else list(PlotMode):
        p.value(data, dest)
