from setuptools import find_packages
from skbuild import setup

with open("README.md", "r") as readme:
    long_description = readme.read()

with open("watchoptical/_version.py") as fp:
    version = {}
    exec(fp.read(), version)
    version = version["__version__"]

setup(name="watchoptical",
      version=version,
      description="WATCHMAN Optical Calibration Analysis Software",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/davehadley/watchoptical",
      author="David Hadley",
      author_email="d.r.hadley@warwick.ac.uk",
      license="MIT",
      packages=find_packages(include=["watchoptical*"]),
      install_requires=["dask>=2.20.0", "toolz>=0.10.0", "distributed>=2.20.0"],
      zip_safe=False,
      classifiers=[
          "Programming Language :: Python :: 3 :: Only",
          "License :: OSI Approved :: MIT License",
          "Development Status :: 2 - Pre-Alpha",
          "Operating System :: POSIX",
          "Intended Audience :: Science/Research",
      ],
      python_requires=">=3.6",
      )

