# watchoptical : WATCHMAN Optical Calibration Analysis Software

## Installation

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
python3 setup.py install
```

If you want to do development work on this package do:
```bash
python3 setup.py develop
```

### Testing you Installation

From the `watchoptical` directory run:
```bash
python -m unittest discover tests
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

## Analyzing WATCHMAN Data 

First run the analysis script on the files that you generated in the previous step:

```bash
python3 -m watchoptical.scripts.runanalysis path/to/input/files/*.root
```

Make plots from the output with:

```bash
python3 -m watchoptical.scripts.plot path/to/input/files/*.root
```