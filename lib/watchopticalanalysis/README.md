# watchoptical calibration analysis 

First run the analysis script on the files that you generated in the previous step:

```bash
python3 -m watchopticalanalysis.scripts.runanalysis path/to/input/files/*.root
```

Make plots from the output with:

```bash
python3 -m watchopticalanalysis.scripts.plot path/to/input/files/*.root
```

Inspect datasets on the command line with:

```bash
python3 -m watchopticalanalysis.scripts.inspectfiles path/to/input/files
```
