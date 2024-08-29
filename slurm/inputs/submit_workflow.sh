#!/bin/bash

# Get the directory of the current script
script_dir=$(dirname "${BASH_SOURCE[0]}")

# Submit the first job from create_dataset.slurm and capture the job ID
job1_id=$(sbatch "${script_dir}/create_dataset.slurm" | awk '{print $4}')

# Submit the second job from train_model.slurm with a dependency on the first job
sbatch --dependency=afterok:"$job1_id" "${script_dir}/train_model.slurm"
