#!/bin/bash --login
#SBATCH -t 0-6
#SBATCH -p serial
#SBATCH -J ERA5-%%JOBID%%

source ~/bin/conda_activate.sh 
conda activate cds-api-0.7.6 


python download.py 2>&1 | tee log_download.txt
