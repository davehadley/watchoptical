from typing import Any, Dict

from setuptools import find_packages
from skbuild import setup

with open("README.md", "r") as readme:
    long_description = readme.read()

with open("watchopticalmc/_version.py") as fp:
    version: Dict[str, Any] = {}
    exec(fp.read(), version)
    version = version["__version__"]

setup(
    name="watchopticalmc",
    version=version,
    description="WATCHMAN Optical Calibration Analysis Software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/davehadley/watchoptical",
    author="David Hadley",
    author_email="d.r.hadley@warwick.ac.uk",
    license="MIT",
    packages=find_packages(include=["watchopticalmc*"]),

    install_requires=[
        "matplotlib",
        "peroose",
        "bokeh",
        "dask[bag,delayed,distributed]>=2.20.0",
        "dask-jobqueue>=0.7.1",
        "toolz>=0.10.0",
        "distributed>=2.20.0",
        "numpy",
        "docopt",
        "fsspec>=0.3.3",
        "boost_histogram",
        "pandas",
        "mplhep",
        "uproot",
        "tabulate",
        "cloudpickle",
        "scipy",
        "sqlitedict",
    ],
    extras_require={
        "dev": ["pre-commit>=2.7.1", "flake8", "mypy", "black", "pytest"],
    },
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 2 - Pre-Alpha",
        "Operating System :: POSIX",
        "Intended Audience :: Science/Research",
    ],
    python_requires=">=3.7",
)
