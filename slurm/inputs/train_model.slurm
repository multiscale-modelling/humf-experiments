#!/bin/bash

#SBATCH --mail-type=ALL
#SBATCH --output=slurm/outputs/%j.out

#SBATCH --partition=a100
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8

echo "Current commit hash:"
git rev-parse HEAD

nvidia-smi
srun dvc repro -s train_model --force
