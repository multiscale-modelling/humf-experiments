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
# >>>

python main.py
module load gromacs
module load orca
dvc repro
