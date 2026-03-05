# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run a model script
python3 pu_learning.py

# Run the visualizer
python3 pu_visualize.py

# Install a new package (system Python on macOS requires this flag)
pip3 install <package> --break-system-packages
```

## Stack

- **Python 3.13** at `/opt/homebrew/bin/python3`
- **Packages:** scikit-learn, pandas, numpy, matplotlib

## Architecture

Each experiment is two scripts: a model file (defines classes, runs evaluation in `main()`) and an optional visualizer that imports from it. `pu_visualize.py` imports `PUBaggingClassifier` directly from `pu_learning.py`.

All datasets and output artifacts go in `data/`.

## Conventions

- Scripts are self-contained and runnable directly via `python3 <file>.py`
- `random_state=42` for reproducibility; `StandardScaler` before model training
- One script per model/experiment — no shared utility modules

## PU Learning notes

- `PUBaggingClassifier` in `pu_learning.py`: default 100 estimators, subsample size = number of labeled positives per round
- Always call `find_threshold()` on a validation set — PU probabilities are not calibrated to 0.5
- ROC-AUC is the primary metric; supplement with F1 at the tuned threshold
