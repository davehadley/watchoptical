from __future__ import annotations

import glob
import hashlib
import os
import re
import subprocess
from collections import OrderedDict
from contextlib import contextmanager
from dataclasses import dataclass, field
from tempfile import TemporaryDirectory
from typing import Any, Callable, Iterator, Optional, Tuple

import cloudpickle
import dask.bag
from dask.bag import Bag
from watchopticalmc.internal.generatemc.makeratdb import RatDb
from watchopticalmc.internal.generatemc.runwatchmakers import (
    WatchMakersConfig,
    generatejobscripts,
)
from watchopticalmc.internal.generatemc.wmdataset import RatPacBonsaiPair
from watchopticalutils.filepathutils import expandpath, temporaryworkingdirectory
from watchopticalutils.retry import retry


@dataclass(frozen=True)
class GenerateMCConfig:
    watchmakersconfig: WatchMakersConfig
    filenamefilter: Optional[Callable[[str], bool]] = None
    npartitions: Optional[int] = None
    partition_size: Optional[int] = None
    numjobs: int = 1
    bonsaiexecutable: str = "${BONSAIDIR}/bonsai"
    bonsailikelihood: str = "${BONSAIDIR}/like.bin"
    injectmacros: Optional[OrderedDict[str, str]] = None
    injectratdb: Optional[OrderedDict[str, RatDb]] = None
    metadata: OrderedDict[str, Any] = field(default_factory=OrderedDict)

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
                hsh.update(v.json.encode())
        return hsh.hexdigest()

    @property
    def configfilename(self):
        dirname = self.watchmakersconfig.directory
        if dirname is None:
            dirname = os.getcwd()
        dirname = os.path.abspath(dirname)
        return f"{dirname}{os.sep}watchopticalconfig_{self.configid}.pickle"

    @classmethod
    def fromfile(cls, filename: str) -> "GenerateMCConfig":
        with open(filename) as f:
            return cloudpickle.load(f)


def _write_config_to_disk(config: GenerateMCConfig):
    os.makedirs(os.path.dirname(config.configfilename), exist_ok=True)
    with open(config.configfilename, "wb") as f:
        cloudpickle.dump(config, f)
    return


def _rungeant4(
    jobnum: int, watchmakersscript: str, cwd: str, config: GenerateMCConfig
) -> Tuple[str, ...]:
    eventtype = re.match(".*/script_(.*).sh", watchmakersscript).group(1)
    expectedfilename = f"run_{config.configid}_{eventtype}_{jobnum}.root"
    with open(watchmakersscript, "r") as script:
        scripttext = script.read()
        with _inject_macros_and_ratdb_into_script(scripttext, config) as scripttext:
            scripttext = scripttext.replace("run$TMPNAME.root", expectedfilename)
            scripttext = scripttext.replace(
                "run$TMPNAME.log", f"run_{config.configid}_{eventtype}_{jobnum}.log"
            )
            match = re.search(f".* -o (root_.*{jobnum}.root) .*", scripttext)
            assert match is not None
            filename = os.sep.join((cwd, match.group(1)))
            if len(tuple(glob.glob(filename))) == 0:
                subprocess.call(scripttext, shell=True, cwd=cwd)
            return tuple(glob.glob(filename))


def _dump_text_to_temp_file(tempdir: str, fname: str, content: Optional[str]) -> str:
    fname = os.sep.join((tempdir, fname))
    content = content if content is not None else ""
    with open(fname, "w") as f:
        f.write(content)
    return fname


def _write_injected_macros_to_disk(
    tempdir: str, injectmacros: OrderedDict[str, str]
) -> OrderedDict[str, str]:
    return OrderedDict(
        (k, _dump_text_to_temp_file(tempdir, k + ".mac", v))
        for k, v in injectmacros.items()
    )


def _write_injected_ratdb_to_disk(
    tempdir: str, injectratdb: OrderedDict[str, RatDb]
) -> OrderedDict[str, str]:
    return OrderedDict(
        (k, _dump_text_to_temp_file(tempdir, k + ".ratdb", v.json))
        for k, v in injectratdb.items()
    )


def _load_ratdb_macro_command(jsoncontents, tempfilename):
    return "\n".join(
        (
            # commented out ratdb contents
            "\n".join(f"# {line}" for line in jsoncontents.split("\n")),
            # macro command to load the file from disk
            f"/rat/db/load {tempfilename}",
        )
    )
    return


@contextmanager
def _inject_macros_and_ratdb_into_script(
    scripttext: str, config: GenerateMCConfig
) -> Iterator[str]:
    injectmacros = config.injectmacros
    injectratdb = config.injectratdb
    with TemporaryDirectory() as tempdir:
        if injectratdb is not None:
            ratdbnames = _write_injected_ratdb_to_disk(tempdir, injectratdb)
            if injectmacros is None:
                injectmacros = OrderedDict()
            injectmacros.update(
                (key, _load_ratdb_macro_command(injectratdb[key].json, fname))
                for key, fname in ratdbnames.items()
            )
            injectmacros["_linktoconfig"] = f"# config-file: {config.configfilename}"
        if injectmacros is not None:
            macronames = _write_injected_macros_to_disk(tempdir, injectmacros)
            s1, s2 = scripttext.split("&& rat")
            scripttext = " ".join([s1, "&& rat"] + list(macronames.values()) + [s2])
        yield scripttext


@retry(3)
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
    _write_config_to_disk(config)
    scripts = generatejobscripts(config.watchmakersconfig)
    cwd = scripts.directory
    return (
        dask.bag.from_sequence(
            (
                (jobnum, s, cwd, config)
                for jobnum in range(config.numjobs)
                for s in scripts.scripts
                if config.filenamefilter is None or config.filenamefilter(s)
            ),
            npartitions=config.npartitions,
            partition_size=config.partition_size,
        )
        .starmap(_rungeant4)
        .flatten()
        .map(lambda g4file: RatPacBonsaiPair(g4file, _runbonsai(g4file, config=config)))
    )
