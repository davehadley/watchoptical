#!/usr/bin/env python

from subprocess import check_call
from pathlib import Path
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-n", "--num", help="Number of tests to run in parallel. Set to auto to use all logical CPU cores.", default=None, type=str)
args = parser.parse_args()

directories = Path("lib").glob("**/tests/")
for directory in directories:
    if args.num:
        check_call(["pytest", "-n", str(args.num), str(directory)])
    else:
        check_call(["pytest", str(directory)])
