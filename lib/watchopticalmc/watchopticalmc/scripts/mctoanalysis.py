import os
from argparse import ArgumentParser, Namespace

from watchopticalmc.internal.generatemc.mctoanalysis import (
    MCToAnalysisConfig,
    mctoanalysis,
)
from watchopticalmc.internal.generatemc.wmdataset import WatchmanDataset
from watchopticalutils.client import ClientType, client
from watchopticalutils.filepathutils import (
    searchforrootfilesexcludinganalysisfiles,
)
from watchopticalmc import AnalysisDataset
from pathlib import Path


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
        analysisfiles = mctoanalysis(
            dataset, config=MCToAnalysisConfig(directory=args.directory)
        ).compute()
    AnalysisDataset(sourcedataset=dataset, 
        analysisfiles=list(analysisfiles),
        directory=Path(args.directory),
        inputfiles=[Path(p) for p in args.inputfiles],
    ).write(Path(args.directory) / "analysisdataset.pickle")
    return


if __name__ == "__main__":
    main()
