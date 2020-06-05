# watchoptical : WATCHMAN Optical Calibration Analysis Software

## Installation

Install the WATCHMAN software following the instructions at:
    
1. WMUtils https://github.com/AIT-WATCHMAN/WMUtils 
2. watchmakers https://github.com/AIT-WATCHMAN/watchmakers/

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

## Generating WATCHMAN MC

To generate MC do:
```bash
python3 -m watchoptical.scripts.generatemc --num-events=1000 --target=local
```
For more options see:
```bash
python3 -m watchoptical.scripts.generatemc --help
```
