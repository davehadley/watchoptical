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

## Analysis files

Finally run:
```bash
python3 -m watchopticalmc.scripts.mctoanalysis path/to/input/files
```
to generate files for analysis.

## Do it all in one step

The three previous steps may be run with:
```bash
python3 -m watchopticalmc 
```
See:
```bash
python3 -m watchopticalmc --help
```
for its arguments.