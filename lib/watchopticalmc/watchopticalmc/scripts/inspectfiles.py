import contextlib  # noqa
import os
import sys
from argparse import ArgumentParser, Namespace
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt  # noqa
import numpy as np  # noqa
from IPython import start_ipython
from traitlets.config import get_config

import watchopticalmc
from watchopticalmc.internal.generatemc.wmdataset import WatchmanDataset
from watchopticalmc.internal.opticsanalysis.analysiseventtuple import AnalysisEventTuple
from watchopticalmc.internal.opticsanalysis.plot import PlotMode
from watchopticalmc.internal.opticsanalysis.runopticsanalysis import (
    OpticsAnalysisResult,
)
from watchopticalmc.internal.utils.cache import cacheget
from watchopticalmc.internal.utils.client import ClientType
from watchopticalmc.internal.utils.filepathutils import (
    searchforrootfilesexcludinganalysisfiles,
)


def parsecml() -> Namespace:
    parser = ArgumentParser(
        description="Process WATCHMAN MC files to the watchopticalmc analysis file "
        "format."
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=os.getcwd(),
        help="Output Directory to store the generated files.",
    )
    parser.add_argument(
        "-p", "--plot", type=lambda s: PlotMode[s], choices=list(PlotMode), default=None
    )
    parser.add_argument(
        "--client",
        "-c",
        type=ClientType,
        choices=list(ClientType),
        default=ClientType.LOCAL,
        help="Where to run jobs.",
    )
    parser.add_argument("inputfiles", nargs="+", type=str, default=[os.getcwd()])
    parser.add_argument("--force", "-f", action="store_true")
    return parser.parse_args()


def loaddata(
    inputfiles: List[str],
) -> Tuple[WatchmanDataset, AnalysisEventTuple, Optional[OpticsAnalysisResult]]:
    dataset = WatchmanDataset(
        f
        for f in searchforrootfilesexcludinganalysisfiles(inputfiles)
        if not ("IBDNeutron" in f or "IBDPosition" in f)
    )
    analysiseventtuple = AnalysisEventTuple.fromWatchmanDataset(dataset)
    try:
        analysisresult = cacheget(f"opticsanalysis/{dataset.name}")
    except KeyError:
        analysisresult = None
    return dataset, analysiseventtuple, analysisresult


if __name__ == "__main__":
    args = parsecml()
    header = f"{__package__} ({watchopticalmc.__version__}) [{watchopticalmc.url}]"
    config = get_config()
    config.InteractiveShellApp.display_banner = False
    config.InteractiveShellApp.exec_lines = [
        # ROOT needed to be imported inside the ipython shell, otherwise GUI won't work.
        "print(header)",
        """with contextlib.suppress(ImportError):
            import ROOT
            from ROOT import TBrowser, TFile
        """,
        "dataset, analysisevents, analysisresult = loaddata(args.inputfiles)",
        'print(f"dataset = {dataset}")',
        'print(f"analysisevents = {analysisevents}")',
        'print(f"analysisresult = {analysisresult}")',
    ]
    sys.exit(start_ipython([], config=config, user_ns={**locals(), **globals()}))
