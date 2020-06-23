import glob
import os
import re
import subprocess
import uuid
from dataclasses import dataclass
from typing import Tuple, Optional, Callable

import dask.bag
from dask.bag import Bag

from watchoptical.internal.runwatchmakers import generatejobscripts, WatchMakersConfig
from watchoptical.internal.wmdataset import RatPacBonsaiPair


@dataclass(frozen=True)
class GenerateMCConfig:
    watchmakersconfig: WatchMakersConfig
    filenamefilter: Optional[Callable[[str], bool]] = None
    npartitions: Optional[int] = None
    partition_size: Optional[int] = None
    numjobs: int = 1


def _rungeant4(watchmakersscript: str, cwd: str, filenamefilter: Optional[Callable[[str], bool]] = None) -> Tuple[str]:
    with open(watchmakersscript) as script:
        scripttext = script.read()
        uid = str(uuid.uuid1())
        scripttext = scripttext.replace("run$TMPNAME.root", f"run{uid}.root")
        scripttext = scripttext.replace("run$TMPNAME.log", f"run{uid}.log")
        filename = os.sep.join((cwd,
                                (re.search(f".* -o (root_.*{uid}.root) .*", scripttext)
                                 .group(1)
                                 )
                                ))
        if filenamefilter is None or filenamefilter(filename):
            subprocess.check_call(scripttext, shell=True, cwd=cwd)
    return tuple(glob.glob(filename))


def _runbonsai(g4file: str) -> str:
    bonsai_name = f"{g4file.replace('root_files', 'bonsai_root_files')}"
    if (not os.path.exists(bonsai_name)) and (g4file != bonsai_name):
        subprocess.check_call(["bonsai", g4file, bonsai_name])
    return bonsai_name


def generatemc(config: GenerateMCConfig) -> Bag:
    scripts = generatejobscripts(config.watchmakersconfig)
    cwd = scripts.directory
    return (dask.bag.from_sequence(((s, cwd, config.filenamefilter) for _ in range(config.numjobs) for s in scripts.scripts),
                                   npartitions=config.npartitions,
                                   partition_size=config.partition_size
                                   )
            .starmap(_rungeant4)
            .flatten()
            .map(lambda g4file: RatPacBonsaiPair(g4file, _runbonsai(g4file)))
            )
