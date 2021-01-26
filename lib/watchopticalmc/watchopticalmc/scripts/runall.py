import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
from subprocess import run

from watchopticalutils.client import ClientType


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
        default=ClientType.CLUSTER,
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
        "--attenuation", help="Set attenuation length.", type=str, default="1.0"
    )
    parser.add_argument(
        "--scattering", help="Set scattering length.", type=str, default="1.0"
    )
    return parser.parse_args()


def main():
    args = _parsecml()
    configurations = [
        (att, scat)
        for att in args.attenuation.split(",")
        for scat in args.attenuation.split(",")
    ]
    # generate MC
    for (attenuation, scattering) in configurations:
        cmd = [
            "python",
            "-m",
            "watchopticalmc.scripts.generatemc",
            f"--num-jobs={args.num_jobs}",
            f"--num-events-per-job={args.num_events_per_job}",
            f"--attenuation={attenuation}",
            f"--scattering={scattering}",
            f"--directory={args.directory}",
            f"--client={args.client.value}",
        ]
        if args.signal_only:
            cmd += ["--signal-only"]
        if args.background_only:
            cmd += ["--background-only"]
        run(cmd, check=True)
    # run sensitivity analysis
    for directory in Path(args.directory).glob("watchmanmc_*"):
        run(
            [
                "python",
                "-m",
                "watchopticalmc.scripts.runsensitivityanalysis",
                f"--client={args.client.value}",
                str(directory),
            ],
            check=True,
        )
    # create analysis files
    run(
        [
            "python",
            "-m",
            "watchopticalmc.scripts.mctoanalysis",
            f"--directory={args.directory}",
            f"--client={args.client.value}",
            str(args.directory),
        ],
        check=True,
    )
    return


if __name__ == "__main__":
    main()
