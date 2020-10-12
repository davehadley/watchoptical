import glob
import hashlib
import os
import re
import subprocess
import typing
import uuid
from collections import OrderedDict
from contextlib import contextmanager
from dataclasses import dataclass
from tempfile import TemporaryDirectory
from typing import Callable, Iterator, Mapping, Optional, Tuple

import dask.bag
from dask.bag import Bag

from watchoptical.internal.runwatchmakers import WatchMakersConfig, generatejobscripts
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
    injectmacros: Optional[typing.OrderedDict[str, str]] = None
    injectratdb: Optional[typing.OrderedDict[str, str]] = None

    def __post_init__(self):
        if not os.path.exists(expandpath(self.bonsaiexecutable)):
            raise ValueError("cannot find bonsai executable", self.bonsaiexecutable)
        if not os.path.exists(expandpath(self.bonsailikelihood)):
            raise ValueError("cannot find bonsai likelihood", self.bonsailikelihood)

    @property
    def configid(self):
        hsh = hashlib.md5()
        if self.injectmacros:
            for k, v in self.injectmacros.items():
                hsh.update(k.encode())
                hsh.update(v.encode())
        if self.injectratdb:
            for k, v in self.injectratdb.items():
                hsh.update(k.encode())
                hsh.update(v.encode())
        return hsh.hexdigest()


def _rungeant4(
    watchmakersscript: str, cwd: str, config: GenerateMCConfig
) -> Tuple[str]:
    with open(watchmakersscript, "r") as script:
        scripttext = script.read()
        uid = str(uuid.uuid1())
        with _inject_macros_and_ratdb_into_script(
            scripttext, config.injectmacros, config.injectratdb
        ) as scripttext:
            scripttext = scripttext.replace(
                "run$TMPNAME.root", f"run_{config.configid}_{uid}.root"
            )
            scripttext = scripttext.replace(
                "run$TMPNAME.log", f"run_{config.configid}_{uid}.log"
            )
            filename = os.sep.join(
                (cwd, (re.search(f".* -o (root_.*{uid}.root) .*", scripttext).group(1)))
            )
            if config.filenamefilter is None or config.filenamefilter(filename):
                subprocess.check_call(scripttext, shell=True, cwd=cwd)
    return tuple(glob.glob(filename))


def _dump_text_to_temp_file(tempdir: str, fname: str, content: str) -> str:
    fname = os.sep.join((tempdir, fname))
    with open(fname, "w") as f:
        f.write(content)
    return fname


def _write_injected_macros_to_disk(
    tempdir: str, injectmacros: typing.OrderedDict[str, str]
) -> typing.OrderedDict[str, str]:
    return OrderedDict(
        (k, _dump_text_to_temp_file(tempdir, k + ".mac", v))
        for k, v in injectmacros.items()
    )


def _write_injected_ratdb_to_disk(
    tempdir: str, injectratdb: typing.OrderedDict[str, str]
) -> typing.OrderedDict[str, str]:
    return OrderedDict(
        (k, _dump_text_to_temp_file(tempdir, k + ".ratdb", v))
        for k, v in injectratdb.items()
    )


def _load_ratdb_macro_command(jsoncontents, tempfilename):
    return "\n".join(
        (
            # commented out ratdb contents
            "\n".join(f"# {l}" for l in jsoncontents.split("\n")),
            # macro command to load the file from disk
            f"/rat/db/load {tempfilename}",
        )
    )
    return


@contextmanager
def _inject_macros_and_ratdb_into_script(
    scripttext: str,
    injectmacros: Optional[typing.OrderedDict[str, str]],
    injectratdb: typing.OrderedDict[str, str],
) -> Iterator[str]:
    with TemporaryDirectory() as tempdir:
        if injectratdb is not None:
            ratdbnames = _write_injected_ratdb_to_disk(tempdir, injectratdb)
            if injectmacros is None:
                injectmacros = OrderedDict()
            injectmacros.update(
                (key, _load_ratdb_macro_command(injectratdb[key], fname))
                for key, fname in ratdbnames.items()
            )
        if injectmacros is not None:
            macronames = _write_injected_macros_to_disk(tempdir, injectmacros)
            s1, s2 = scripttext.split("&& rat")
            scripttext = " ".join([s1, "&& rat"] + list(macronames.values()) + [s2])
        yield scripttext


def _runbonsai(g4file: str, config: GenerateMCConfig) -> str:
    bonsai_name = f"{g4file.replace('root_files', 'bonsai_root_files')}"
    with temporaryworkingdirectory():
        os.symlink(
            expandpath(config.bonsailikelihood), f"{os.getcwd()}{os.sep}like.bin"
        )
        if (not os.path.exists(bonsai_name)) and (g4file != bonsai_name):
            subprocess.check_call(
                [expandpath(config.bonsaiexecutable), g4file, bonsai_name]
            )
    return bonsai_name


def generatemc(config: GenerateMCConfig) -> Bag:
    scripts = generatejobscripts(config.watchmakersconfig)
    cwd = scripts.directory
    return (
        dask.bag.from_sequence(
            ((s, cwd, config) for _ in range(config.numjobs) for s in scripts.scripts),
            npartitions=config.npartitions,
            partition_size=config.partition_size,
        )
        .starmap(_rungeant4)
        .flatten()
        .map(lambda g4file: RatPacBonsaiPair(g4file, _runbonsai(g4file, config=config)))
    )
