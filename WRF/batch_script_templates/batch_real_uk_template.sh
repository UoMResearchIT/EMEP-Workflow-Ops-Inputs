#!/bin/bash --login

# SPDX-FileCopyrightText: 2025 - 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

#SBATCH -t 0-2
#SBATCH -p multicore_small
#SBATCH -n 6
#SBATCH -J REAL-UK-%%JOBID%%

module load apps/gcc/wrf/4.5

CWD=%%WRFDIR%%
WPS_DIR=%%WPSDIR%%


WPS_NAME='WPS_METGRID_45km'
WORK_NAME='UK_REAL_45km'


WORK_PATH=${CWD}/${WORK_NAME}
WPS_PATH=${WPS_DIR}/${WPS_NAME}

cd ${WORK_PATH}

ln -s ${WPS_PATH}/met_em.* .


time mpirun -np 6 real.exe
