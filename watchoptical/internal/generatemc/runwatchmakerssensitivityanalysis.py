import os
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from glob import glob
from typing import List, NamedTuple

from watchoptical.internal.generatemc.runwatchmakers import path_to_watchmakers_script


@dataclass(frozen=True)
class WatchMakersSensitivityAnalysisConfig:
    inputdirectory: str


class WatchMakersSensitivityResult(NamedTuple):
    s: float
    b: float
    t3sigma: float
    metric: float


def runwatchmakerssensitivityanalysis(
    config: WatchMakersSensitivityAnalysisConfig, force: bool = False
) -> WatchMakersSensitivityResult:
    if force or not len(_get_sensitvity_files(config.inputdirectory)) > 0:
        logs = _run_all_watchmakers_steps(config.inputdirectory)
        _write_logs(logs, config.inputdirectory)
    return loadwatchmakerssensitvity(config.inputdirectory)


def _get_sensitvity_files(directory: str) -> List[str]:
    return glob(f"{directory}{os.sep}results_*.txt")


def loadwatchmakerssensitvity(directory: str) -> WatchMakersSensitivityResult:
    return _parse_watchmakers_result_txt(_get_sensitvity_files(directory)[0])


class WatchMakersSensitivityStep(Enum):
    MERGESTEP = "-M"
    EFFICIENCY = "--histograms"
    RATES = "--evalRate"
    FINDRATES = "--findRate"


def _run_watchmakers_script(directory: str, step: WatchMakersSensitivityStep) -> str:
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return subprocess.check_output(
        [
            "python3",
            path_to_watchmakers_script(),
            "--lassen",
            step.value,
            "--enableRoot",
        ],
        text=True,
        cwd=directory,
    )


def _run_all_watchmakers_steps(directory: str) -> List[str]:
    return [
        _run_watchmakers_script(directory, step) for step in WatchMakersSensitivityStep
    ]


def _write_logs(logs: List[str], directory: str) -> str:
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    filename = f"{directory}{os.sep}log.watchmakers.sensitvity.txt"
    with open(filename, "w") as f:
        for s in logs:
            f.write(s)
    return filename


def _parse_watchmakers_result_txt(filename: str) -> WatchMakersSensitivityResult:
    text = open(filename).readlines()[0]
    pattern = "^.+ .+ .+ .+ (.*?) (.+?) (.+?) (.+?)$"
    (s, b, t3sigma, metric) = map(
        float, re.match(pattern, text).groups()  # type: ignore
    )
    return WatchMakersSensitivityResult(s=s, b=b, t3sigma=t3sigma, metric=metric)
