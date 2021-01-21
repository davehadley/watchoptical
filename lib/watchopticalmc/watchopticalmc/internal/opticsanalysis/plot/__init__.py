from enum import Enum
from functools import partial
from typing import Optional

from watchopticalmc.internal.opticsanalysis.plot.dumpselectiontables import (
    dumpselectiontables,
)
from watchopticalmc.internal.opticsanalysis.plot.plotattenuation import plotattenuation
from watchopticalmc.internal.opticsanalysis.plot.plothist import plothist
from watchopticalmc.internal.opticsanalysis.plot.plotscatter import plotscatter
from watchopticalmc.internal.opticsanalysis.runopticsanalysis import (
    OpticsAnalysisResult,
)


class PlotMode(Enum):
    hist = partial(plothist)
    scatter = partial(plotscatter)
    attenuation = partial(plotattenuation)
    dumpselectionstats = partial(dumpselectiontables)


def plot(data: OpticsAnalysisResult, dest: str, mode: Optional[PlotMode] = None):
    for p in [mode] if mode is not None else list(PlotMode):
        p.value(data, dest)
