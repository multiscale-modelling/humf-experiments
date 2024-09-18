# HUMF experiments

## Installation

Install this project with [poetry](https://python-poetry.org).
Note the use of the `git clone --recursive` to clone the `humf` submodule dependency.
Note that if you have a virtual environment activated (e.g. a `conda` environment), `poetry install` will install this project and its dependencies into that environment. Otherwise, poetry will create a virtual environment.

```
git clone --recursive git@gitlab.kit.edu:kit/ag_wenzel/humf-experiments.git
cd humf-experiments
poetry install
```

Activate the environment.
Note that this is not necessary if you had a virtual environment active when running `poetry install`.

```
poetry shell
```

If you intend to contribute, install [pre-commit](https://pre-commit.com) hooks:

```
pre-commit install
```

## Running the workflow

Run `sbatch slurm/inputs/submit_workflow.slurm` to run the workflow. Alternatively, details on how to run the workflow manually are given below.

To set up the DVC pipeline, run `python main.py`. Rerun this command whenever you make changes to `main.py`. Note that ZnTrack only ever adds stages to or overrides stages in `dvc.yaml`. Thus, when removing stages from `main.py`, you may also want to remove them from `dvc.yaml`.

Once the DVC pipeline is up-to-date, it can be run using `dvc repro` or `dvc exp run`. Consult the DVC docs on these commands for further details. Before running a stage, make sure to load the required software dependencies, i.e. activate the poetry environment for this project and use `module load gromacs` and `module load orca`. Ignore warnings that say PyTorch can't find NVIDIA drivers, the workflow nodes request computational resources including GPUs as necessary.

The `dvc repro` and `dvc exp run` commands will only run stages with changed dependencies, unless the `--force` option is given. Whenever running a stage creates or modifies output files in `nodes/`, DVC automatically commits the new files to the cache and updates the corresponding placeholder files tracked by git. This is then visible in the output of `git status`. See also the output of `dvc data status` and `dvc status`. To commit the changes, `git commit` and `git push` the placeholder files and `dvc push` the data files to the remote storage. To revert the changes, use `git checkout .` and `dvc checkout`.

## Testing

Run tests with [pytest](https://docs.pytest.org).
Note the use of `cd tests`, so that node test output is separated from node workflow output.

```
cd tests
pytest
```

## Contributing

The pre-commit tool uses [ruff](https://github.com/astral-sh/ruff) to lint and format Python files, and [isort](https://pycqa.github.io/isort/) to sort imports in Python files. Consider integrating these tools into your workflow, e.g. using the vscode plugins for [ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) and [isort](https://marketplace.visualstudio.com/items?itemName=ms-python.isort).
