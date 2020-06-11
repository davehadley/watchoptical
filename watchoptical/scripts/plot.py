from argparse import ArgumentParser, Namespace

from watchoptical import watchopticalcpp
from watchoptical.internal.utils import findfiles
from watchoptical.internal.wmdataset import WatchmanDataset


def parsecml() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--inputfiles", nargs="+", type=str, default=["~/work/wm/data/testwatchoptical/attempt01/*_files_default/*/*.root"])
    return parser.parse_args()


def plot():
    watchopticalcpp.hello("?")
    return


def main():
    args = parsecml()
    dataset = WatchmanDataset(args.inputfiles)
    plot()
    return


if __name__ == '__main__':
    main()
