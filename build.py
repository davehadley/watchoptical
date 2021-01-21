#!/usr/bin/env python
from pathlib import Path
from subprocess import check_call
import multiprocessing


def run(cmd, title=None):
    if title is None:
        title = "Running:" + " ".join(cmd)
    print("--- {}".format(title))
    print(" ".join(cmd))
    check_call(cmd)
    return


Path("build").mkdir(exist_ok=True)

def buildratpac():
    run(["sed", "-i", "s/CMAKE_CXX_STANDARD 11/CMAKE_CXX_STANDARD 17/g", "external/rat-pac/CMakeLists.txt"])
    run(
        [
            "cmake",
            "-Bbuild/rat-pac",
            "external/rat-pac",
        ],
        "CMake rat-pac",
    )
    run(["cmake", "--build", "build/rat-pac", "--parallel", str(multiprocessing.cpu_count())])
    return


def buildbonsai():
    run(["sed", "-i", "s/CMAKE_CXX_STANDARD 11/CMAKE_CXX_STANDARD 17/g", "external/bonsai/CMakeLists.txt"])
    run(
        [
            "cmake",
            "-Bbuild/bonsai",
            "external/bonsai",
            "-DCMAKE_CXX_STANDARD=17",
        ],
        "CMake bonsai",
    )
    run(["cmake", "--build", "build/bonsai", "--parallel", str(multiprocessing.cpu_count())])
    return

def buildwatchoptical():
    run(["pip", "install", "-e", ".[dev]"], "Install watchoptical")


def main():
    buildratpac()
    buildbonsai()
    buildwatchoptical()
    return


if __name__ == "__main__":
    main()
