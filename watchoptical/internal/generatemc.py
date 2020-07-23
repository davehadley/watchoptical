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
from watchoptical.internal.utils import expandpath, temporaryworkingdirectory
from watchoptical.internal.wmdataset import RatPacBonsaiPair


@dataclass(frozen=True)
class GenerateMCConfig:
    watchmakersconfig: WatchMakersConfig
    filenamefilter: Optional[Callable[[str], bool]] = None
    npartitions: Optional[int] = None
    partition_size: Optional[int] = None
    numjobs: int = 1
    bonsaiexecutable: str = "${BONSAIDIR}/bonsai"
    bonsailikelihood: str = "${BONSAIDIR}/like.bin"

    def __post_init__(self):
        if not os.path.exists(expandpath(self.bonsaiexecutable)):
            raise ValueError("cannot find bonsai executable", self.bonsaiexecutable)
        if not os.path.exists(expandpath(self.bonsailikelihood)):
            raise ValueError("cannot find bonsai likelihood", self.bonsailikelihood)


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


def _runbonsai(g4file: str, config: GenerateMCConfig) -> str:
    bonsai_name = f"{g4file.replace('root_files', 'bonsai_root_files')}"
    with temporaryworkingdirectory():
        os.symlink(expandpath(config.bonsailikelihood), f"{os.getcwd()}{os.sep}like.bin")
        if (not os.path.exists(bonsai_name)) and (g4file != bonsai_name):
            subprocess.check_call([expandpath(config.bonsaiexecutable), g4file, bonsai_name])
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
            .map(lambda g4file: RatPacBonsaiPair(g4file, _runbonsai(g4file, config=config)))
            )
