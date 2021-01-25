import os
from argparse import ArgumentParser, Namespace

from watchopticalmc import WatchmanDataset
from watchopticalanalysis.internal.plot import PlotMode, plot
from watchopticalanalysis.internal.runopticsanalysis import (
    cachedopticsanalysis,
)
from watchopticalutils.client import ClientType, client
from watchopticalutils.filepathutils import (
    searchforrootfilesexcludinganalysisfiles,
)


def parsecml() -> Namespace:
    parser = ArgumentParser(
        description="Process WATCHMAN analysis files to generate plots."
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


def main():
    args = parsecml()
    dataset = WatchmanDataset(
        f
        for f in searchforrootfilesexcludinganalysisfiles(args.inputfiles)
        if not ("IBDNeutron" in f or "IBDPosition" in f)
    )
    with client(args.client):
        result = cachedopticsanalysis(dataset, forcecall=args.force)
    plot(data=result, dest=os.sep.join((args.directory, "plots")), mode=args.plot)
    return


if __name__ == "__main__":
    main()
