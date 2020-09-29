import os
from argparse import ArgumentParser, Namespace

from watchoptical.internal import watchopticalcpp
from watchoptical.internal.client import ClientType, client
from watchoptical.internal.mctoanalysis import mctoanalysis, MCToAnalysisConfig
from watchoptical.internal.utils import findfiles, searchforrootfilesexcludinganalysisfiles
from watchoptical.internal.wmdataset import WatchmanDataset


def parsecml() -> Namespace:
    parser = ArgumentParser(description="Process WATCHMAN MC files to the watchoptical analysis file format.")
    parser.add_argument("-d", "--directory", type=str, default=os.getcwd(),
                        help="Output Directory to store the generated files.")
    parser.add_argument("--client", "-c", type=ClientType, choices=list(ClientType),
                        default=ClientType.LOCAL,
                        help="Where to run jobs."
                        )
    parser.add_argument("inputfiles", nargs="+", type=str, default=[os.getcwd()])
    return parser.parse_args()


def main():
    args = parsecml()
    dataset = WatchmanDataset(searchforrootfilesexcludinganalysisfiles(args.inputfiles))
    with client(args.client):
        mctoanalysis(dataset, config=MCToAnalysisConfig(directory=args.directory)).compute()
    return


if __name__ == '__main__':
    main()
