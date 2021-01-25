#!/usr/bin/env python

from subprocess import check_call
from pathlib import Path

directories = Path("lib").glob("**/tests/")
for directory in directories:
    check_call(["pytest", str(directory)])
