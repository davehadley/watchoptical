import glob
import os
import re
import subprocess
from dataclasses import dataclass
from itertools import zip_longest
from typing import Tuple, List, Optional, Callable, NamedTuple

import dask.bag
from dask.bag import Bag
from dask.delayed import Delayed

from watchoptical.internal.runwatchmakers import generatejobscripts, WatchMakersConfig

class RatPacBonsaiPair(NamedTuple):
    g4file: str
    bonsaifile: str


@dataclass(frozen=True)
class GenerateMCConfig:
    watchmakersconfig: WatchMakersConfig
    filenamefilter: Optional[Callable[[str], bool]] = None
    npartitions: Optional[int] = None
    partition_size: Optional[int] = None


def _rungeant4(watchmakersscript: str, cwd: str, filenamefilter: Optional[Callable[[str], bool]] = None) -> Tuple[str]:
    with open(watchmakersscript) as script:
        filename = os.sep.join((cwd,
                                (re.search(r".* -o (root_.*\$TMPNAME.root) .*", script.read())
                                 .group(1)
                                 .replace("$TMPNAME", "*")
                                 )
                                ))
    if filenamefilter is None or filenamefilter(filename):
        subprocess.check_call([watchmakersscript], cwd=cwd)
    return tuple(glob.glob(filename))


def _runbonsai(g4file: str) -> str:
    bonsai_name = f"{g4file.replace('root_files', 'bonsai_root_files')}"
    if (not os.path.exists(bonsai_name)) and (g4file != bonsai_name):
        subprocess.check_call(["bonsai", g4file, bonsai_name])
    return bonsai_name


def generatemc(config: GenerateMCConfig) -> Bag:
    scripts = generatejobscripts(config.watchmakersconfig)
    cwd = scripts.directory
    return (dask.bag.from_sequence(((s, cwd, config.filenamefilter) for s in scripts.scripts),
                                   npartitions=config.npartitions,
                                   partition_size=config.partition_size
                                   )
            .starmap(_rungeant4)
            .flatten()
            .map(lambda g4file: RatPacBonsaiPair(g4file, _runbonsai(g4file)))
            )
