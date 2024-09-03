#!/bin/bash

if ! [ -f pyproject.toml ]; then
  echo "Error: workflow was not submitted from the project root directory."
  exit 1
fi

# <<< git
if [ -n "$(git status --porcelain)" ]; then
  echo "Error: git status is not clear."
  exit 1
fi
echo "Current commit hash:"
git rev-parse HEAD
# >>>

# <<< poetry
# shellcheck disable=SC1091
source "$(poetry env info --path)/bin/activate"
# >>>

# <<< dvc
if ! dvc data status -q; then
  echo "Error: dvc data status is not clear."
  exit 1
fi
if ! dvc status -q; then
  echo "Error: dvc status is not clear."
  exit 1
fi
python main.py
# >>>

# Get the directory of the current script
script_dir=$(dirname "${BASH_SOURCE[0]}")

# Submit the first job from create_dataset.slurm and capture the job ID
job1_id=$(sbatch "${script_dir}/create_dataset.slurm" | awk '{print $4}')

# Submit the second job from train_model.slurm with a dependency on the first job
sbatch --dependency=afterok:"$job1_id" "${script_dir}/train_model.slurm"
