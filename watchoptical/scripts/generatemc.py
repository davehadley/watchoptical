import os
import sys
from argparse import ArgumentParser, Namespace
from enum import Enum
from typing import Optional, Any
from collections import OrderedDict

from dask.distributed import LocalCluster, Client
from dask.system import cpu_count
from distributed.system import memory_limit

from watchoptical.internal.client import ClientType, client
from watchoptical.internal.generatemc import generatemc, GenerateMCConfig
from watchoptical.internal.makeratdb import makeratdb
from watchoptical.internal.ratmacro import ratmacro
from watchoptical.internal.runwatchmakers import WatchMakersConfig
from watchoptical.internal.utils import expandpath


def _parsecml() -> Namespace:
    parser = ArgumentParser(description="Generate WATCHMAN MC files")
    parser.add_argument("--directory", "-d", type=str, default=os.getcwd(),
                        help="Directory to store generated files. It will be created if it does not exist."
                        )
    parser.add_argument("--target", "-t", type=ClientType, choices=list(ClientType),
                        default=ClientType.SINGLE,
                        help="Where to run jobs."
                        )
    parser.add_argument("--signal-only", action="store_true")
    parser.add_argument("--num-events-per-job", "-n", type=int, default=10000,
                        help="Number of events per sub-job to generate for each source of signal/background type."
                        )
    parser.add_argument("--num-jobs", "-j", type=int, default=100,
                        help="Number of sub-jobs to generate for each source of signal/background type."
                        )
    parser.add_argument("--bonsai",
                        help="Path to the bonsai executable. Environment variable ${BONSAIDIR}/bonsai is used if not set.",
                        default="${BONSAIDIR}/bonsai")
    parser.add_argument("--bonsai-likelihood",
                        help="Path to the bonsai likelihood. Environment variable ${BONSAIDIR}/like.bin is used if not set.",
                        default="${BONSAIDIR}/like.bin")
    parser.add_argument("--attenuation",
                        help="Set attenuation length.",
                        type=float,
                        default=None
                        )
    parser.add_argument("--scattering",
                        help="Set scattering length.",
                        type=float,
                        default=None
                        )
    return parser.parse_args()


def _validatearguments(args):
    if not os.path.exists(expandpath(args.bonsai)):
        print(f"Cannot find bonsai executable {args.bonsai}")
        sys.exit(1)
    if not os.path.exists(expandpath(args.bonsai_likelihood)):
        print(f"Cannot find bonsai likelihood {args.bonsai_likelihood}")
        sys.exit(1)
    return


def _wrapindict(key: str, value: Any):
    if (value is not None):
        return OrderedDict({key: value})
    else:
        return None


def _getconfigdir(args: Namespace) -> str:
    suffix = ""
    if args.attenuation is not None:
        suffix += f"_attenuation{args.attenuation:.5e}"
    if args.scattering is not None:
        suffix += f"_scattering{args.scattering:.5e}"
    if suffix == "":
        suffix = "_nominal"
    return "watchmanmc" + suffix


def _run(args):
    directory = args.directory + os.sep + _getconfigdir(args)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    filenamefilter = None if args.signal_only is None else lambda f: "IBD_LIQUID_pn" in f
    injectratdb = _wrapindict(f"attenuation_{args.attenuation}",
                              makeratdb(attenuation=args.attenuation, scattering=args.scattering))
    config = GenerateMCConfig(WatchMakersConfig(directory=directory, numevents=args.num_events_per_job),
                              numjobs=args.num_jobs,
                              bonsaiexecutable=expandpath(args.bonsai),
                              bonsailikelihood=expandpath(args.bonsai_likelihood),
                              injectratdb=injectratdb,
                              filenamefilter=filenamefilter
                              )
    with client(args.target):
        generatemc(config).compute()


def main():
    args = _parsecml()
    _validatearguments(args)
    _run(args)
    return


if __name__ == "__main__":
    main()
