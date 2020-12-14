#!/usr/bin/env python
import os
from subprocess import check_call


def run(cmd, title):
    print("--- {}".format(title))
    print(" ".join(cmd))
    check_call(cmd)
    return


os.mkdir("build", exist_ok=True)


def buildratpac():
    run(
        [
            "cmake",
            "-Bbuild/rat-pac",
            "externals/ratpac",
            "-DCMAKE_CXX_STANDARD=17",
        ],
        "CMake rat-pac",
    )
    run(["cmake", "--build", "build/rat-pac"])
    return


def buildwatchoptical():
    run(["pip" "install" "-e" "./watchoptical"], "Install watchoptical")


def main():
    buildratpac()
    buildwatchoptical()


if __name__ == "__main__":
    main()
