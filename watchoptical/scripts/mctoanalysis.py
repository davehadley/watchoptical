import os
from argparse import ArgumentParser, Namespace

from watchoptical.internal import watchopticalcpp
from watchoptical.internal.client import ClientType, client
from watchoptical.internal.mctoanalysis import mctoanalysis, MCToAnalysisConfig
from watchoptical.internal.utils import findfiles
from watchoptical.internal.wmdataset import WatchmanDataset


def parsecml() -> Namespace:
    parser = ArgumentParser(description="Process WATHCMAN MC files to the watchoptical analysis file format.")
    parser.add_argument("-d", "--directory", type=str, default=os.getcwd(),
                        help="Output Directory to store the generated files.")
    parser.add_argument("--target", "-t", type=ClientType, choices=list(ClientType),
                        default=ClientType.SINGLE,
                        help="Where to run jobs."
                        )
    parser.add_argument("--inputfiles", nargs="+", type=str, default=[
        "~/work/wm/data/testwatchoptical/attempt01/*_files_default/*IBD_LIQUID_pn_ibd*/*.root"])
    return parser.parse_args()


def main():
    args = parsecml()
    dataset = WatchmanDataset(args.inputfiles)
    with client(args.target):
        mctoanalysis(dataset, config=MCToAnalysisConfig(directory=args.directory)).compute()
    return


if __name__ == '__main__':
    main()
