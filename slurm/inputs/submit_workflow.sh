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
# >>>

# <<< poetry
# shellcheck disable=SC1091
source "$(poetry env info --path)/bin/activate"
# >>>

# <<< dvc
# if ! dvc data status -q; then
#   echo "Error: dvc data status is not clear."
#   exit 1
# fi
# if ! dvc status -q; then
#   echo "Error: dvc status is not clear."
#   exit 1
# fi
python main.py
# >>>

# Get the directory of the current script
script_dir=$(dirname "${BASH_SOURCE[0]}")

# We assume that the workflow can be split into two sections:
# The first section generates datasets from MD simulations and DFT
# calculations. The second section trains machine learning models on the
# generated datasets. We assume that all stages in the first section require
# approximately the same amount of CPU resources, and that all stages in the
# second section require approximately the same amount of GPU resources. Thus,
# we submit each section as an individual Slurm job.

# Submit the first job and capture the job ID
job1_id=$(sbatch "${script_dir}/cpu_stages.slurm" | awk '{print $4}')

# Submit the second job with a dependency on the first job
sbatch --dependency=afterok:"$job1_id" "${script_dir}/gpu_stages.slurm"
