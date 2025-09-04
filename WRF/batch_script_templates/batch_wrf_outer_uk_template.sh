#!/bin/bash --login
#SBATCH -t 1-6
#SBATCH -p multicore
#SBATCH -n 36
#SBATCH -J WRF-OUTERUK-%%JOBID%%

module load apps/gcc/wrf/4.5

CWD=%%WRFDIR%%

WORK_NAME='UK_WRF_45km'
REAL_NAME='UK_REAL_45km'


WORK_PATH=${CWD}/${WORK_NAME}

cd ${WORK_PATH}

# we are running in a separate directory to REAL, so link to the input files
ln -s ${CWD}/${REAL_NAME}/wrfbdy_d01 .
ln -s ${CWD}/${REAL_NAME}/wrfinput_d01 .
ln -s ${CWD}/${REAL_NAME}/wrffdda_d01 .
ln -s ${CWD}/${REAL_NAME}/wrflowinp_d01 .
# for domain 2
ln -s ${CWD}/${REAL_NAME}/wrfinput_d02 .
ln -s ${CWD}/${REAL_NAME}/wrflowinp_d02 .


# run the domains with different numbers of processes (due to differing domain sizes)
rm rsl.error.* rsl.out.*
time mpirun -np 36 wrf.exe
