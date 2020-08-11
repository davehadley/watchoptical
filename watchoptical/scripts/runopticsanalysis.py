import os
from argparse import ArgumentParser, Namespace

from watchoptical.internal.client import ClientType, client
from watchoptical.internal.runopticsanalysis import shelvedopticsanalysis
from watchoptical.internal.utils import searchforrootfilesexcludinganalysisfiles
from watchoptical.internal.wmdataset import WatchmanDataset


def parsecml() -> Namespace:
    parser = ArgumentParser(description="Analyze WATCHMAN data files.")
    parser.add_argument("-d", "--directory", type=str, default=os.getcwd(),
                        help="Output Directory to store the generated files.")
    parser.add_argument("--target", "-t", type=ClientType, choices=list(ClientType),
                        default=ClientType.SINGLE,
                        help="Where to run jobs."
                        )
    parser.add_argument("inputfiles", nargs="+", type=str, default=[os.getcwd()])
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main():
    args = parsecml()
    dataset = WatchmanDataset(f for f in searchforrootfilesexcludinganalysisfiles(args.inputfiles)
                              if not ("IBDNeutron" in f or "IBDPosition" in f)
                              )
    with client(args.target):
        shelvedopticsanalysis(dataset, forcecall=True)
    return


if __name__ == '__main__':
    main()
