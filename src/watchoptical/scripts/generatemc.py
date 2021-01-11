import os
import sys
from argparse import ArgumentParser, Namespace
from collections import OrderedDict
from typing import Any, Callable, Optional

from watchoptical.internal.generatemc.generatemc import GenerateMCConfig, generatemc
from watchoptical.internal.generatemc.makeratdb import makeratdb
from watchoptical.internal.generatemc.runwatchmakers import WatchMakersConfig
from watchoptical.internal.stringconstants import StringConstants
from watchoptical.internal.utils.client import ClientType, client
from watchoptical.internal.utils.filepathutils import expandpath


def _parsecml() -> Namespace:
    parser = ArgumentParser(description="Generate WATCHMAN MC files")
    parser.add_argument(
        "--directory",
        "-d",
        type=str,
        default=os.getcwd(),
        help="Directory to store generated files. "
        "It will be created if it does not exist.",
    )
    parser.add_argument(
        "--client",
        "-c",
        type=ClientType,
        choices=list(ClientType),
        default=ClientType.SINGLE,
        help="Where to run jobs.",
    )
    parser.add_argument("--signal-only", action="store_true")
    parser.add_argument("--background-only", action="store_true")
    parser.add_argument(
        "--num-events-per-job",
        "-n",
        type=int,
        default=10000,
        help="Number of events per sub-job to generate for each source of "
        "signal/background type.",
    )
    parser.add_argument(
        "--num-jobs",
        "-j",
        type=int,
        default=100,
        help="Number of sub-jobs to generate for each source of signal/background "
        "type.",
    )
    parser.add_argument(
        "--bonsai",
        help="Path to the bonsai executable. Environment variable ${BONSAIDIR}/bonsai "
        "is used if not set.",
        default="${BONSAIDIR}/bonsai",
    )
    parser.add_argument(
        "--bonsai-likelihood",
        help="Path to the bonsai likelihood. Environment variable "
        "${BONSAIDIR}/like.bin is used if not set.",
        default="${BONSAIDIR}/like.bin",
    )
    parser.add_argument(
        "--attenuation", help="Set attenuation length.", type=float, default=None
    )
    parser.add_argument(
        "--scattering", help="Set scattering length.", type=float, default=None
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
    if value is not None:
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


def _filenamefilterfromargs(args: Namespace) -> Optional[Callable[[str], bool]]:
    if args.signal_only:
        return lambda f: StringConstants.WATCHMAKERS_SIGNAL_PATTERN in f
    elif args.background_only:
        return lambda f: StringConstants.WATCHMAKERS_SIGNAL_PATTERN not in f
    else:
        return None


def _run(args):
    directory = args.directory + os.sep + _getconfigdir(args)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    filenamefilter = _filenamefilterfromargs(args)
    injectratdb = _wrapindict(
        f"attenuation_{args.attenuation}_scattering_{args.scattering}",
        makeratdb(attenuation=args.attenuation, scattering=args.scattering),
    )
    config = GenerateMCConfig(
        WatchMakersConfig(directory=directory, numevents=args.num_events_per_job),
        numjobs=args.num_jobs,
        bonsaiexecutable=expandpath(args.bonsai),
        bonsailikelihood=expandpath(args.bonsai_likelihood),
        injectratdb=injectratdb,
        filenamefilter=filenamefilter,
    )
    with client(args.client):
        generatemc(config).compute()


def main():
    args = _parsecml()
    _validatearguments(args)
    _run(args)
    return


if __name__ == "__main__":
    main()
