#!/bin/bash

#SBATCH --mail-type=ALL
#SBATCH --output=slurm/outputs/%j.out

#SBATCH --mem=32G

echo "Current commit hash:"
git rev-parse HEAD

module load gromacs
module load orca

# Use one `dvc repro` command for each cpu stage that is a leaf (i.e. not a
# dependency of any other stage) of the cpu subgraph (i.e. the workflow graph
# if all gpu stages are removed).
srun dvc repro CreateGromacsDataset
srun dvc repro CreateOrcaDataset

# You can force a single cpu stage to run using -sf, e.g.
# srun dvc repro -sf CreateGromacsDataset

# You can force a stage and all its dependencies to run using -f, e.g.
# srun dvc repro -f CreateGromacsDataset
