import os
from argparse import ArgumentParser, Namespace
from typing import Any
from collections import OrderedDict

from watchoptical.internal.client import ClientType, client
from watchoptical.internal.utils import expandpath
from watchoptical.internal.runwatchmakerssensitivityanalysis import WatchMakersSensitivityAnalysisConfig, \
    runwatchmakerssensitivityanalysis


def _parsecml() -> Namespace:
    parser = ArgumentParser(description="Calculate sensitivity with WATCHMAKER")
    parser.add_argument("--input-directory", "-i", type=str, default=os.getcwd(),
                        help="Directory containing input WATCHMAN MC files to be included in the sensitivity analysis."
                        )
    parser.add_argument("--output-directory", "-o", type=str, default=os.getcwd(),
                        help="Directory to store generated files. It will be created if it does not exist."
                        )
    parser.add_argument("--target", "-t", type=ClientType, choices=list(ClientType),
                        default=ClientType.SINGLE,
                        help="Where to run jobs."
                        )
    return parser.parse_args()


def _validatearguments(args):
    return


def _wrapindict(key: str, value: Any):
    if (value is not None):
        return OrderedDict({key: value})
    else:
        return None


def _run(args):
    if not os.path.exists(args.directory):
        os.makedirs(args.directory, exist_ok=True)
    with client(args.target):
        config = WatchMakersSensitivityAnalysisConfig(inputdirectory=expandpath(args.input_directory),
                                                      outputdirectory=expandpath(args.output_directory),
                                                      )
        runwatchmakerssensitivityanalysis(config).compute()


def main():
    args = _parsecml()
    _validatearguments(args)
    _run(args)
    return


if __name__ == "__main__":
    main()
