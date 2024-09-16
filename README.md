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

To set up the DVC pipeline, run `python main.py`. Rerun this command whenever you make changes to `main.py`. Note that ZnTrack only ever adds stages to or overrides stages in `dvc.yaml`. Thus, when removing stages from `main.py`, you may also want to remove them from `dvc.yaml`.

To run the workflow locally, use `dvc repro`. Note that the workflow consists of two parts: A CPU-demanding part that generates datasets and a GPU-demanding part that trains models. To run these parts individually on a Slurm cluster, use `sbatch slurm/inputs/cpu_stages.slurm` and `sbatch slurm/inputs/gpu_stages.slurm` respectively. To run the full workflow, use `bash slurm/inputs/submit_workflow.sh`. The latter submits the two Slurm scripts in the correct order. The slurm scripts run the necessary `dvc repro` commands. For more fine-grained control over what exactly gets executed, see also the comments in the files in `slurm/inputs/`, as well as the [documentation](https://dvc.org/doc/command-reference/repro) of `dvc repro`.


## Testing

Run tests with [pytest](https://docs.pytest.org).
Note the use of `cd tests`, so that node test output is separated from node workflow output.

```
cd tests
pytest
```

## Contributing

The pre-commit tool uses [ruff](https://github.com/astral-sh/ruff) to lint and format Python files, and [isort](https://pycqa.github.io/isort/) to sort imports in Python files. Consider integrating these tools into your workflow, e.g. using the vscode plugins for [ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) and [isort](https://marketplace.visualstudio.com/items?itemName=ms-python.isort).
