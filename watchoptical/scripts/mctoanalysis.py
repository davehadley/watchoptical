import os
from argparse import ArgumentParser, Namespace

from watchoptical.internal.generatemc.mctoanalysis import (
    MCToAnalysisConfig,
    mctoanalysis,
)
from watchoptical.internal.generatemc.wmdataset import WatchmanDataset
from watchoptical.internal.utils.client import ClientType, client
from watchoptical.internal.utils.filepathutils import (
    searchforrootfilesexcludinganalysisfiles,
)


def parsecml() -> Namespace:
    parser = ArgumentParser(
        description="Process WATCHMAN MC files to the watchoptical analysis file "
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
        "--client",
        "-c",
        type=ClientType,
        choices=list(ClientType),
        default=ClientType.LOCAL,
        help="Where to run jobs.",
    )
    parser.add_argument("inputfiles", nargs="+", type=str, default=[os.getcwd()])
    return parser.parse_args()


def main():
    args = parsecml()
    dataset = WatchmanDataset(searchforrootfilesexcludinganalysisfiles(args.inputfiles))
    with client(args.client):
        mctoanalysis(
            dataset, config=MCToAnalysisConfig(directory=args.directory)
        ).compute()
    return


if __name__ == "__main__":
    main()
