#!/bin/bash

#SBATCH --mail-type=ALL
#SBATCH --output=slurm/outputs/%j.out

#SBATCH --mem=32G

module load gromacs
module load orca
srun dvc repro create_dataset
