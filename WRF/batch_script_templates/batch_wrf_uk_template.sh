#!/bin/bash --login
#SBATCH -t 1-6
#SBATCH -p hpcpool
#SBATCH -A hpc-dt-targ
#SBATCH -N 5
#SBATCH -n 160
#SBATCH -J WRF-UK-%%JOBID%%

module load apps/gcc/wrf/4.5

CWD=%%WRFDIR%%

WORK_NAME='UK_3km'
NDOWN_NAME='UK_NDOWN_3km'
REAL_NAME='UK_REAL_45km'

WORK_PATH=${CWD}/${WORK_NAME}
NDOWN_PATH=${CWD}/${NDOWN_NAME}
REAL_PATH=${CWD}/${REAL_NAME}

cd ${WORK_PATH}

ln -s ${NDOWN_PATH}/wrfinput_d02 wrfinput_d01
ln -s ${NDOWN_PATH}/wrfbdy_d02 wrfbdy_d01
ln -s ${REAL_PATH}/wrflowinp_d03 wrflowinp_d01

# run the domains with different numbers of processes (due to differing domain sizes)
rm rsl.error.* rsl.out.*
time mpirun -np 144 wrf.exe
