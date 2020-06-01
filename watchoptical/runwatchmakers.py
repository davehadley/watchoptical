import glob
import os
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Iterable, Tuple


@dataclass(frozen=True)
class WatchMakersScripts:
    scripts: Tuple[str]


def path_to_watchmakers_script() -> str:
    return os.sep.join((os.environ['WATCHENV'],
                        "watchmakers.py"
                        ))


def generatejobscripts(directory: str = None) -> WatchMakersScripts:
    if directory is None:
        directory = tempfile.mkdtemp(prefix="watchoptical_runwatchmakers")
    _run_watchmakers_script(directory=directory)
    scripts = tuple(glob.glob(os.path.sep.join((directory,
                                                os.path.sep.join(["job", "script_*.sh"])
                                                ))))
    return WatchMakersScripts(scripts=scripts)


def _run_watchmakers_script(directory: str = None):
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    subprocess.check_call(["python3",
                           path_to_watchmakers_script(),
                           "-m",
                           "-j",
                           "--lassen"
                           ],
                          cwd=directory)
