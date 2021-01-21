#!/usr/bin/env python
from shutil import which
from subprocess import check_call


def testcommand(cmd, title):
    print("--- {}".format(title))
    print(" ".join(cmd))
    check_call(cmd)
    return

def checkbonsai():
    print("--- Check bonsai")
    bonsai = which("bonsai")
    print(bonsai)
    if bonsai is None:
        raise Exception("can't find bonsai executable")
    return

def checkwatchoptical():
    print("--- Check watchoptical")
    import watchoptical
    print(watchoptical)

if __name__ == "__main__":
    testcommand(["env"], "Environemnt Variables")
    testcommand(["root", "-q", "-l"], "Check ROOT")
    testcommand(["rat", "--help"], "Check RAT")
    checkbonsai()
    checkwatchoptical()

