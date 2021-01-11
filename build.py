#!/usr/bin/env python
from pathlib import Path
from subprocess import check_call


def run(cmd, title):
    print("--- {}".format(title))
    print(" ".join(cmd))
    check_call(cmd)
    return


Path("build").mkdir(exist_ok=True)


def buildratpac():
    run(
        [
            "cmake",
            "-Bbuild/rat-pac",
            "external/ratpac",
            "-DCMAKE_CXX_STANDARD=17",
        ],
        "CMake rat-pac",
    )
    run(["cmake", "--build", "build/rat-pac"])
    return


def buildbonsai():
    run(
        [
            "cmake",
            "-Bbuild/bonsai",
            "external/bonsai",
            "-DCMAKE_CXX_STANDARD=17",
        ],
        "CMake bonsai",
    )
    return

def buildwatchoptical():
    run(["pip" "install" "-e" "./watchoptical"], "Install watchoptical")


def main():
    buildratpac()
    buildbonsai()
    buildwatchoptical()


if __name__ == "__main__":
    main()
