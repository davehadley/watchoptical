# watchoptical : WATCHMAN Optical Calibration Analysis Software

## Installation

Clone the git repository with:

```bash
git clone  --recurse-submodules git@github.com:davehadley/watchoptical.git
```

Setup up the environment with:

```bash
source setup-environment.sh
```

Run this setup script each time that you want to work with the package.

Build the package and dependencies with:

```bash
python build.py
```

This should build `rat-pac` (<https://github.com/AIT-WATCHMAN/WMUtils>), 
`watchmakers` (<ttps://github.com/AIT-WATCHMAN/watchmakers/>) and 
`FRED` / `bonsai` (<https://github.com/AIT-WATCHMAN/FRED>).

## Old Installation Instructions

Install the WATCHMAN software following the instructions at:
    
1. WMUtils https://github.com/AIT-WATCHMAN/WMUtils 
2. watchmakers https://github.com/AIT-WATCHMAN/watchmakers/
3. Standalone BONSAI https://github.com/AIT-WATCHMAN/bonsai/
    1. watchoptical requires a ${BONSAIDIR} environment variable to find
    the correct BONSAI version. You should set this in your environment setup. 

Check out this package:

```bash
git clone https://github.com/davehadley/watchoptical
cd watchoptical
./post-clone.sh
pip install .
```

If you want to do development work on this package do:
```bash
python setup.py develop
```

Note editable installs with `pip` do not work on my system:
```
pip install -e .
```

### Testing you Installation

From the `watchoptical` directory run:
```bash
pytest tests
```

## Generating WATCHMAN MC

To generate MC do:
```bash
python3 -m watchoptical.scripts.generatemc --num-events=1000 --target=local
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
python3 -m watchoptical.scripts.inspect path/to/input/files
```