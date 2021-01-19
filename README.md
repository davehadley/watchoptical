# watchoptical : WATCHMAN Optical Calibration Analysis Software

## Checking out the code

Clone the git repository with:

```bash
git clone  --recurse-submodules git@github.com:davehadley/watchoptical.git
```

If you have an old version of git you may have to run:

```
git clone git@github.com:davehadley/watchoptical.git
git submodule update --init --recursive
```

The git submodules in this repository use https authentication.
If you prefer to use ssh authentication with github, you may wish to consider applying this setting:

```bash
git config --global url.ssh://git@github.com/.insteadOf https://github.com/
```

## Installation

Setup up the environment with:

```bash
source setup-environment.sh
```

Run this setup script each time that you want to work with the package.
It may be slow the first time that it is run, but it should run quickly.

Build the package and dependencies with:

```bash
python build.py
```

This should build `rat-pac` (<https://github.com/AIT-WATCHMAN/WMUtils>), 
`watchmakers` (<ttps://github.com/AIT-WATCHMAN/watchmakers/>) and 
`FRED` / `bonsai` (<https://github.com/AIT-WATCHMAN/FRED>).

Check that that was successful with:

```bash
python test-environment.py
```

If that script produces errors, then something when wrong.

If you are still having trouble contact @davehadley.

### Testing your Installation

From the `watchoptical` directory run:
```bash
pytest tests
```

## Generating WATCHMAN MC

To generate MC do:
```bash
python3 -m watchoptical.scripts.generatemc --client=cluster
```
For more options see:
```bash
python3 -m watchoptical.scripts.generatemc --help
```

## Running the Standard WATCHMAN WatchMakers sensitivity analysis 

```bash
python3 -m watchoptical.scripts.runsensitivityanalysis path/to/input/files
```

## Analyzing WATCHMAN Data 

First run the analysis script on the files that you generated in the previous step:

```bash
python3 -m watchoptical.scripts.runanalysis path/to/input/files/*.root
```

Make plots from the output with:

```bash
python3 -m watchoptical.scripts.plot path/to/input/files/*.root
```

Inspect datasets on the command line with:

```bash
python3 -m watchoptical.scripts.inspectfiles path/to/input/files
```

## Development Instructions

Please install the pre-commit hooks before doing any development work.
You can install this by running the command:
```
pre-commit install
```