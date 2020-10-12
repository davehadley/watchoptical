import os
from argparse import ArgumentParser, Namespace

from watchoptical.internal.client import ClientType, client
from watchoptical.internal.opticsanalysis.runopticsanalysis import shelvedopticsanalysis
from watchoptical.internal.utils import searchforrootfilesexcludinganalysisfiles
from watchoptical.internal.wmdataset import WatchmanDataset


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
        shelvedopticsanalysis(dataset, forcecall=True)
    return


if __name__ == "__main__":
    main()
