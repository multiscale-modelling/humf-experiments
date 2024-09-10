#!/bin/bash

#SBATCH --mail-type=ALL
#SBATCH --output=slurm/outputs/%j.out

#SBATCH --partition=a100
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8

echo "Current commit hash:"
git rev-parse HEAD

nvidia-smi
srun dvc repro -fs TrainModel
srun dvc repro -fs TrainModel_1
srun dvc repro -fs EvaluateModels
srun dvc repro -fs EvaluateModels_1
