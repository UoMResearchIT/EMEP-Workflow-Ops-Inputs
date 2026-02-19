#!/bin/bash --login

# SPDX-FileCopyrightText: 2025 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

#SBATCH -t 0-12
#SBATCH -p serial
#SBATCH -J ERA5-%%JOBID%%

source ~/bin/conda_activate.sh 
conda activate cds-api-0.7.6 


python download.py 2>&1 | tee log_download.txt
