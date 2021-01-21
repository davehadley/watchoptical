import os
from argparse import ArgumentParser, Namespace

from watchoptical.internal.generatemc.wmdataset import WatchmanDataset
from watchoptical.internal.opticsanalysis.runopticsanalysis import cachedopticsanalysis
from watchoptical.internal.utils.client import ClientType, client
from watchoptical.internal.utils.filepathutils import (
    searchforrootfilesexcludinganalysisfiles,
)


def parsecml() -> Namespace:
    parser = ArgumentParser(description="Analyze WATCHMAN data files.")
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=os.getcwd(),
        help="Output Directory to store the generated files.",
    )
    parser.add_argument(
        "--client",
        "-c",
        type=ClientType,
        choices=list(ClientType),
        default=ClientType.CLUSTER,
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
        cachedopticsanalysis(dataset, forcecall=True)
    return


if __name__ == "__main__":
    main()
