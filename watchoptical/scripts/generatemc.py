import os
from argparse import ArgumentParser, Namespace
from enum import Enum

from dask.distributed import LocalCluster, Client
from dask.system import cpu_count
from distributed.system import memory_limit

from watchoptical.internal.client import ClientType, client
from watchoptical.internal.generatemc import generatemc, GenerateMCConfig
from watchoptical.internal.runwatchmakers import WatchMakersConfig


def _parsecml() -> Namespace:
    parser = ArgumentParser(description="Generate WATCHMAN MC files")
    parser.add_argument("--directory", "-d", type=str, default=os.getcwd(),
                        help="Directory to store generated files. It will be created if it does not exist."
                        )
    parser.add_argument("--target", "-t", type=ClientType, choices=list(ClientType),
                        default=ClientType.LOCAL,
                        help="Where to run jobs."
                        )
    parser.add_argument("--num-events", "-n", type=int, default=1000,
                        help="Number of events to generate for each source of signal/background type."
                        )
    return parser.parse_args()


def main():
    args = _parsecml()
    if not os.path.exists(args.directory):
        os.makedirs(args.directory, exist_ok=True)
    config = GenerateMCConfig(WatchMakersConfig(directory=args.directory, numevents=args.num_events))
    with client(args.target):
        generatemc(config).compute()
    return


if __name__ == "__main__":
    main()
