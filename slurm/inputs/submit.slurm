#!/bin/bash

#SBATCH --mail-type=ALL
#SBATCH --output=slurm/outputs/%j.out

if ! ls | grep -qE '^pyproject\.toml$'; then
    echo "Error: sbatch was not run from the project root directory."
    exit 1
fi

# <<< git
if ! [ -z "$(git status --porcelain)" ]; then
    echo "Error: git status is not clear."
    exit 1
else
    echo "Current commit hash:"
    git rev-parse HEAD
fi
# >>>

# <<< poetry
source $(poetry env info --path)/bin/activate
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
# >>>

module load gromacs
module load orca
srun echo "Hello from sbatch!"
