# Lab 2 - Model training and experiment tracking with MLflow

## Question 1
After running `uv add mlflow torch torchvision scikit-learn`, `pyproject.toml` now lists `mlflow`, `torch`, `torchvision` and `scikit-learn` as dependencies. `uv.lock` grew much longer, recording the exact resolved versions of all 101 packages needed, including every sub-dependency.

## Question 2
`--backend-store-uri` tells mlflow where to store the run **metadata** (params, metrics, tags, run status) — here a local SQLite file `mlflow.db`. `--default-artifact-root` tells mlflow where to store the **artifacts** (actual files produced by a run, like the saved model) — here the local `./mlruns` folder. The difference: metadata is small, structured data mlflow queries to build the UI (tables, charts); artifacts are the larger output files (models, plots, etc.) saved to disk and just referenced by the metadata.

## Question 3
`mlflow.db` and `mlruns/` shouldn't be tracked by git because they are local run outputs that change every time training is run — they're not source code, and committing them would bloat the repo history and cause constant diffs/conflicts. They shouldn't be tracked by dvc either because dvc is meant for versioning the actual dataset used for training, not regenerable experiment logs and metadata tied to one machine's local mlflow server.

## Question 4
The first time `mlflow.set_experiment("food11")` is called with a name that doesn't exist yet, mlflow automatically creates a new experiment with that name (confirmed by the log line: `Experiment with name 'food11' does not exist. Creating a new experiment.`). It then shows up in the mlflow UI under Experiments.

## Question 5
`mlflow.log_param` records a fixed setting chosen before training starts (e.g. learning rate, batch size) — a single value that doesn't change during the run. `mlflow.log_metric` records a value produced during training that can evolve over time (e.g. loss, accuracy). `log_metric` takes a `step` argument so mlflow can plot how the value changes across epochs/iterations; `log_param` doesn't need `step` because it's logged once and stays constant for the whole run.

## Question 6
Opening a run in the mlflow UI shows:
- **Parameters**: dataset, epochs, lr, batch_size, model
- **Metrics**: train_loss, val_loss, val_accuracy (each with a chart across epochs) and test_accuracy (single final value)
- **Artifacts tab**: shows the saved `model` folder

On disk, the model artifact lives under `mlruns/<experiment_id>/<run_id>/artifacts/model/` in the project folder, matching the `--default-artifact-root` passed to the server.

## Question 7
Results from the 4 runs (dataset=mini, batch_size=32 unless noted):
- lr=0.01 → val_accuracy ≈ 0.130
- lr=0.001 → val_accuracy ≈ 0.565
- lr=0.0001 → val_accuracy ≈ 0.726
- lr=0.001, batch_size=64 → val_accuracy ≈ 0.484

The best val_accuracy came from lr=0.0001. Higher learning rate is not always better — in fact lr=0.01 performed far worse than the smaller rates, likely because such a large learning rate destabilized training and prevented good convergence in only 5 epochs.

## Question 8
The parallel coordinates plot (axes: batch_size, lr, val_accuracy) shows a clear pattern: runs with a **low lr** end up with **high val_accuracy** (yellow/orange lines on the high end of the color scale), while the run with **lr=0.01** drops sharply to a **low val_accuracy** (dark blue/purple line at the bottom). `batch_size` shows no clear relationship with val_accuracy — both batch sizes tested (32 and 64) appear on both high- and low-accuracy lines. This suggests lr was the dominant hyperparameter in this set of experiments.

## Question 9
Sorting the runs table by val_accuracy descending, the best run is **worried-perch-38** (lr=0.0001, batch_size=32, dataset=mini), with val_accuracy ≈ 0.7263 and test_accuracy ≈ 0.7564.

**Run ID: 5daa99fdc19a4ba0855bfb6d4cbdcee4**