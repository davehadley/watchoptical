from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from subprocess import run
from typing import Dict, Iterable, Iterator, List

import watchopticalreport2020.resources


@dataclass
class Report:
    name: str
    formats: Dict[str, Path]


def generatereport(
    inputpath: Path, outputpath: Path, formats: Iterable[str] = ("html", "pdf")
) -> Report:
    name = _generate_name()
    with _gather_input_files(inputpath) as inputfiles:
        formats = {
            ext: _run_pandoc(name, inputfiles, outputpath, ext) for ext in formats
        }
        return Report(name=name, formats=formats)


def _generate_name() -> str:
    return "watchopticalreport"


def _run_pandoc(
    name: str, inputfiles: Iterable[Path], outputpath: Path, toext: str
) -> Path:
    outputfilename = outputpath / f"{name}.{toext}"
    run(
        ["pandoc", f"--output={outputfilename}"] + [str(f) for f in inputfiles],
        check=True,
    )
    return outputfilename


@contextmanager
def _gather_input_files(inputpath: Path) -> Iterator[List[Path]]:
    with ExitStack() as stack:
        filenames = ["001_introduction.md"]
        yield [
            stack.enter_context(resources.path(watchopticalreport2020.resources, fname))
            for fname in filenames
        ]
