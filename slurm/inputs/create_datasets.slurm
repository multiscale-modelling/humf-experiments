#!/bin/bash

#SBATCH --mail-type=ALL
#SBATCH --output=slurm/outputs/%j.out

#SBATCH --mem=32G

echo "Current commit hash:"
git rev-parse HEAD

module load gromacs
module load orca
srun dvc repro CreateGromacsDataset
srun dvc repro CreateOrcaDataset
