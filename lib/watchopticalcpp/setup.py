from typing import Any, Dict

from setuptools import find_packages
from skbuild import setup

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="watchopticalcpp",
    version="0.3.0",
    description="Python C++ extensions for WATCHMAN Optical Calibration analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/davehadley/watchoptical",
    author="David Hadley",
    author_email="d.r.hadley@warwick.ac.uk",
    license="MIT",
    packages=find_packages(include=["watchopticalcpp*"]),
    install_requires=[],
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
    python_requires=">=3.8",
)
