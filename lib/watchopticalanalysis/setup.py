from typing import Any, Dict

from setuptools import setup, find_packages

with open("README.md", "r") as readme:
    long_description = readme.read()

with open("src/watchopticalanalysis/_version.py") as fp:
    version: Dict[str, Any] = {}
    exec(fp.read(), version)
    version = version["__version__"]

setup(
    name="watchopticalanalysis",
    version=version,
    description="WATCHMAN Optical Calibration Analysis Software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/davehadley/watchoptical",
    author="David Hadley",
    author_email="d.r.hadley@warwick.ac.uk",
    license="MIT",
    packages=find_packages(include=["watchopticalanalysis*"]),
    install_requires=[
        "watchopticalmc",
    ],
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 2 - Pre-Alpha",
        "Operating System :: POSIX",
        "Intended Audience :: Science/Research",
    ],
    python_requires=">=3.8",
)
