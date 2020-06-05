import glob
import os
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass(frozen=True)
class WatchMakersConfig:
    numevents: int = 1000
    directory: Optional[str] = None


@dataclass(frozen=True)
class WatchMakersScripts:
    scripts: Tuple[str]
    directory: str


def path_to_watchmakers_script() -> str:
    return os.sep.join((os.environ['WATCHENV'],
                        "watchmakers.py"
                        ))


def generatejobscripts(config: WatchMakersConfig = None) -> WatchMakersScripts:
    if config is None:
        config = WatchMakersConfig()
    directory = config.directory if config.directory is not None else tempfile.mkdtemp(prefix="watchoptical_runwatchmakers")
    _run_watchmakers_script(directory=directory, numevents=config.numevents)
    scripts = tuple(glob.glob(os.path.sep.join((directory,
                                                os.path.sep.join(["job", "script_*.sh"])
                                                ))))
    return WatchMakersScripts(scripts=scripts, directory=directory)


def _run_watchmakers_script(directory: str = None, numevents: int = 2500):
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    subprocess.check_call(["python3",
                           path_to_watchmakers_script(),
                           "-m",
                           "-j",
                           "--lassen",
                           "-e", str(numevents),
                           ],
                          cwd=directory)
