import logging
import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Iterable, Optional

from watchopticalanalysis.algorithm import Algorithm, cached_apply_algorithms
from watchopticalanalysis.algs import AlgDefs
from watchopticalmc import AnalysisDataset, AnalysisEventTuple
from watchopticalutils.client import ClientType, client

_log = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
    args = parsecml()
    _validateargs(args)
    dataset = _build_dataset(args.dataset)
    _log.info("running: {}".format(args.alg if args.alg else "all"))
    alg = _csalgsnames_to_list(args.alg, args.output)
    with client(args.client):
        cached_apply_algorithms(
            alg,
            AnalysisEventTuple.fromAnalysisDataset(dataset).filter(
                lambda x: x is not None
            ),
            force=args.force,
        )


def parsecml() -> Namespace:
    parser = ArgumentParser("Run watchopticalanalysis")
    parser.add_argument(
        "--alg",
        "-a",
        help=(
            "Comma separated list of algorithms to run. "
            "If not set, all algorithms will be run."
        ),
        type=str,
        default=None,
    )
    parser.add_argument(
        "-c",
        "--client",
        help="Where to run jobs.",
        type=ClientType,
        choices=list(ClientType),
        default=ClientType.LOCAL,
    )
    parser.add_argument(
        "dataset",
        help='A directory to process or the path to an "analysisdataset.pickle" file.',
        type=Path,
        default=Path("./"),
    )
    parser.add_argument("-o", "--output", type=Path, default=Path("./"))
    parser.add_argument(
        "--force",
        "-f",
        help="Do not use cached results. Force data processing.",
        action="store_true",
    )
    args = parser.parse_args()
    if args.dataset is None:
        args.dataset = Path(".")
    return args


def _csalgsnames_to_list(csv: Optional[str], output: Path) -> Iterable[Algorithm]:
    kwargs = {"output": output / "plots"}
    if csv is None:
        return list(alg.value(**kwargs) for alg in AlgDefs)
    try:
        return [AlgDefs[algname].value(**kwargs) for algname in csv.split(",")]
    except KeyError as ex:
        validnames = [a.name for a in AlgDefs]
        _log.error(f'Unknown algorithm: "{ex}". Must be one of: "{validnames}"')
        exit(1)


def _validateargs(args: Namespace):
    if not args.dataset.exists():
        _log.error(f'Dataset does not exist: "{args.dataset}".')
        exit(1)


def _build_dataset(path: Path):
    return AnalysisDataset.load(path)


if __name__ == "__main__":
    main()
