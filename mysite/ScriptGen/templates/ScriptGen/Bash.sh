#!/bin/bash 

##SBATCH Lines for Resource Request ##

#SBATCH --time=10:00:00
#SBATCH --nodes=2
#SBATCH --tasks=2
#SBATCH --mem-per-cpu=1 Gb
#SBATCH --job-name ML Task
##Command Lines to Run ## 

cd /path/
srun -n 5 Classifier.py
