from argparse import ArgumentParser, Namespace
from pathlib import Path
import os
from watchopticalmc.internal.generatemc.wmdataset import WatchmanDataset
from watchopticalutils.filepathutils import searchforrootfilesexcludinganalysisfiles
from watchopticalmc import AnalysisDataset

def parsecml() -> Namespace:
    parser = ArgumentParser(
        description="Generate an index of WATCHMAN MC files."
    )
    parser.add_argument("-o", "--output", type=str, default="analysisdataset.pickle")
    parser.add_argument("directory",
        type=str,
        default=os.getcwd(),
        help="Directory containing MC files to index.",
    )
    return parser.parse_args()


def main():
    args = parsecml()
    dataset = WatchmanDataset(searchforrootfilesexcludinganalysisfiles([args.directory]))
    analysisfiles = list(Path(args.directory).glob("watchopticalanalysis*.root"))
    d = AnalysisDataset(sourcedataset=dataset, 
        analysisfiles=list(analysisfiles),
        directory=Path(args.directory),
        inputfiles=list(str(f) for t in dataset for f in t),
    )
    d.write(Path(args.output))
    assert AnalysisDataset.load(Path(args.output))
    return

if __name__ == "__main__":
    main()