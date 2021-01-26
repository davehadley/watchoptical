from enum import Enum
from functools import partial
from typing import Optional

from watchopticalanalysis.internal.plot.plotattenuation import plotattenuation
from watchopticalanalysis.internal.plot.plothist import plothist
from watchopticalanalysis.internal.plot.plotscatter import plotscatter
from watchopticalanalysis.internal.runopticsanalysis import OpticsAnalysisResult


class PlotMode(Enum):
    hist = partial(plothist)
    scatter = partial(plotscatter)
    attenuation = partial(plotattenuation)


def plot(data: OpticsAnalysisResult, dest: str, mode: Optional[PlotMode] = None):
    for p in [mode] if mode is not None else list(PlotMode):
        p.value(data, dest)
