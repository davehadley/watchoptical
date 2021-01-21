# watchopticalmc : Generate WATCHMAN MC for Optical calibration analysis

## Setup

Set-up your environment according to the [instructions at the top level](../../README.md) of this git repository.

## Installation

Install with pip:

```bash
pip install -e ./lib/watchopticalmc[dev]
```

An editable install is recommended.
If you are having trouble contact @davehadley.

### Testing your Installation

We use the pytest testing framework:

```bash
pytest tests
```

## Generating WATCHMAN MC

To generate MC do:
```bash
python3 -m watchopticalmc.scripts.generatemc --client=cluster
```
For more options see:
```bash
python3 -m watchopticalmc.scripts.generatemc --help
```

## Running the Standard WATCHMAN WatchMakers sensitivity analysis 

```bash
python3 -m watchopticalmc.scripts.runsensitivityanalysis path/to/input/files
```

## Analyzing WATCHMAN Data 

TODO this should be moved to a separate package.

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
