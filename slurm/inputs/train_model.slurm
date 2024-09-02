#!/bin/bash

#SBATCH --mail-type=ALL
#SBATCH --output=slurm/outputs/%j.out

#SBATCH --partition=a100
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8

if ! [ -f pyproject.toml ]; then
	echo "Error: sbatch was not run from the project root directory."
	exit 1
fi

# <<< git
#if [ -n "$(git status --porcelain)" ]; then
#	echo "Error: git status is not clear."
#	exit 1
#fi
#echo "Current commit hash:"
#git rev-parse HEAD
# >>>

# <<< poetry
# shellcheck disable=SC1091
source "$(poetry env info --path)/bin/activate"
# >>>

# <<< dvc
# if ! dvc data status -q; then
# 	echo "Error: dvc data status is not clear."
# 	exit 1
# fi

# if ! dvc status -q; then
# 	echo "Error: dvc status is not clear."
# 	exit 1
# fi
# >>>

nvidia-smi
srun dvc repro -s train_model --force
