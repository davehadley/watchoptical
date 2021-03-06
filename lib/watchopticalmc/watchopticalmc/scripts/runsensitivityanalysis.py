import os
from argparse import ArgumentParser, Namespace
from collections import OrderedDict
from typing import Any

import dask.bag
from toolz import curry

from watchopticalmc.internal.generatemc.runwatchmakerssensitivityanalysis import (
    WatchMakersSensitivityAnalysisConfig,
    WatchMakersSensitivityResult,
    runwatchmakerssensitivityanalysis,
)
from watchopticalutils.client import ClientType, client
from watchopticalutils.filepathutils import expandpath


def _parsecml() -> Namespace:
    parser = ArgumentParser(description="Calculate sensitivity with WATCHMAKER")
    parser.add_argument(
        "input_directories",
        type=str,
        nargs="+",
        help="Directories containing input WATCHMAN MC files to be included in the "
        "sensitivity analysis.",
    )
    parser.add_argument(
        "--client",
        "-c",
        type=ClientType,
        choices=list(ClientType),
        default=ClientType.SINGLE,
        help="Where to run jobs.",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Run jobs even if there is already a pre-existing result stored.",
    )
    return parser.parse_args()


def _validatearguments(args):
    for directory in args.input_directories:
        if not os.path.exists(directory):
            raise ValueError(f"directory {directory} does not exist")
    return


def _wrapindict(key: str, value: Any):
    if value is not None:
        return OrderedDict({key: value})
    else:
        return None


def _run(args):
    with client(args.client):
        dask.bag.from_sequence(args.input_directories).map(
            _processdir(force=args.force)
        ).compute()


@curry
def _processdir(directory: str, force: bool = False) -> WatchMakersSensitivityResult:
    config = WatchMakersSensitivityAnalysisConfig(inputdirectory=expandpath(directory))
    return runwatchmakerssensitivityanalysis(config, force=force)


def main():
    args = _parsecml()
    _validatearguments(args)
    _run(args)
    return


if __name__ == "__main__":
    main()
