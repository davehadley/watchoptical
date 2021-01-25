import os
from argparse import ArgumentParser, Namespace

from watchopticalmc import AnalysisDataset, WatchmanDataset
from watchopticalanalysis.internal.runopticsanalysis import (
    cachedopticsanalysis,
)
from watchopticalutils.client import ClientType, client
from watchopticalutils.filepathutils import (
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
    parser.add_argument("inputdataset", type=str, default=os.getcwd()+"/analysisdataset.pickle")
    parser.add_argument("--force", "-f", action="store_true")
    return parser.parse_args()


def main():
    args = parsecml()
    dataset = AnalysisDataset.load(args.dataset)
    with client(args.client):
        cachedopticsanalysis(dataset, forcecall=True)
    return


if __name__ == "__main__":
    main()
