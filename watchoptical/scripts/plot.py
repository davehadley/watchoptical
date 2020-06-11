from argparse import ArgumentParser, Namespace

import uproot as uproot

from watchoptical.internal.utils import findfiles
from watchoptical.internal.wmdataset import WatchmanDataset


def parsecml() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--inputfiles", nargs="+", type=str, default=["~/work/wm/data/testwatchoptical/attempt01/*_files_default/*IBD_LIQUID_pn*/*.root"])
    return parser.parse_args()

def load(dataset):
    for f in dataset:
        print(f)
        g4file = uproot.open(f.g4file)
        print(g4file)
        #interpretation = uproot.asjagged(uproot.astable(uproot.asdtype([(' fBits', '>u8'), (' fUniqueID', '>u8'), ('id', '>i4'), ('charge', '>f4'), ('time', '>f8')], [('id', '<i4'), ('charge', '<f4'), ('time', '<f8')])), 10)
        g4file.showstreamers()
        g4file["T"].show()
        #arr = g4file["T"]["ev"].array()
        for offset in range(0, 1000):
            try:
                interpretation = uproot.asjagged(uproot.asdtype(
                [(' fBits', '>u8'), (' fUniqueID', '>u8'), ('id', '>i4'), ('charge', '>f4'), ('time', '>f8')],
                [('id', '<i4'), ('charge', '<f4'), ('time', '<f8')]), offset)
                arr = g4file["T"]["ev.pmt"].array(interpretation)
                print(arr)
            except AssertionError:
                pass
        #df = uproot.daskframe(f.g4file, "T")
        #print(df)
        print(arr)
        print(arr)


def plot():
    return


def main():
    args = parsecml()
    dataset = WatchmanDataset(args.inputfiles)
    load(dataset)
    plot()
    return


if __name__ == '__main__':
    main()
