#!/bin/bash

#SBATCH --mail-type=ALL
#SBATCH --output=slurm/outputs/%j.out

#SBATCH --partition=a100
#SBATCH --gres=gpu:1

# Note: This script requests a GPU to avoid warnings that say PyTorch can't
# find NVDIA drivers. Apart from that, the requested resources do not matter.
# This script runs the workflow through DVC, and each workflow stage submits
# its own Slurm job, requesting resources as necessary.

if ! [ -f pyproject.toml ]; then
  echo "Error: workflow was not submitted from the project root directory."
  exit 1
fi

# <<< poetry
# shellcheck disable=SC1091
source "$(poetry env info --path)/bin/activate"
# >>>

module load gromacs
module load orca
dvc exp run
