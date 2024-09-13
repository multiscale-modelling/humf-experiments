#!/bin/bash

#SBATCH --mail-type=ALL
#SBATCH --output=slurm/outputs/%j.out

#SBATCH --partition=a100
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8

echo "Current commit hash:"
git rev-parse HEAD

nvidia-smi

# Use dvc repro to run all gpu stages.
# This assumes that all cpu stages have results cached for their current
# inputs and parameters and will thus be skipped by DVC.
srun dvc repro

# You can force a single gpu stage to run using -fs, e.g.
# srun dvc repro -fs TrainModel

# Note that you can not force a gpu stage and its dependencies to run.
# This would run cpu nodes without the necessary resources.
