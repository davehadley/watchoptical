#!/usr/bin/env python

from subprocess import check_call
from pathlib import Path

directories = [
    dir
    for lib in ("watchopticalutils", "watchopticalcpp", "watchopticalmc", "watchopticalanalysis")
    for dir in (f"lib/{lib}/{lib}", f"lib/{lib}/tests")
]
for directory in directories:
    check_call(["black", "--check", str(directory)])
    check_call(["mypy", "--no-strict-optional", "--ignore-missing-imports", str(directory)])
    check_call(["flake8", str(directory)])

