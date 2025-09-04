#!/bin/bash --login
#SBATCH -t 0-3
#SBATCH -p hpcpool
#SBATCH -A hpc-dt-targ
#SBATCH -N 5
#SBATCH -n 160
#SBATCH -J WRF-EU-%%JOBID%%

module load apps/gcc/wrf/4.5

CWD=%%WRFDIR%%


WORK_NAME='EMEP_WRF_50km'
REAL_NAME='EMEP_REAL_50km'

WORK_PATH=${CWD}/${WORK_NAME}

cd ${WORK_PATH}

# the EMEP simulation needs more setup, because we are running in a separate directory to REAL
ln -s ${CWD}/${REAL_NAME}/wrfbdy_d01 .
ln -s ${CWD}/${REAL_NAME}/wrfinput_d01 .
ln -s ${CWD}/${REAL_NAME}/wrffdda_d01 .
ln -s ${CWD}/${REAL_NAME}/wrflowinp_d01 .

# run the domains with different numbers of processes (due to differing domain sizes)
rm rsl.error.* rsl.out.*
time mpirun -np 153 wrf.exe
