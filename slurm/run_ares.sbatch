#!/bin/bash -l
#SBATCH --job-name=fakenews_mc
#SBATCH --partition=plgrid
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --time=00:30:00
#SBATCH --array=0-1
#SBATCH --output=logs/slurm_%A_%a.out
#SBATCH --error=logs/slurm_%A_%a.err



module load python/3.10.4-gcccore-11.3.0
source venv/bin/activate

python src/run.py --runs 25000 --workers 48 --task-id $SLURM_ARRAY_TASK_ID