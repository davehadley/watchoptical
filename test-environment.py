#!/usr/bin/env python
from subprocess import check_call


def testcommand(cmd, title):
    print("--- {}".format(title))
    print(" ".join(cmd))
    check_call(cmd)
    return


testcommand(["env"], "Environemnt Variables")
testcommand(["root", "-q", "-l"], "Check ROOT")
testcommand(["rat", "--help"], "Check RAT")

print("--- Check watchoptical")
import watchoptical

print(watchoptical)
