import re

from watchoptical.internal.mctoanalysis import AnalysisFile


def eventtypefromfile(file: AnalysisFile) -> str:
    fname = file.producedfrom.g4file
    try:
        result = re.match(".*/Watchman_(.*)/.*", fname).group(1)
    except AttributeError:
        result = "unknown"
    return result