#!/bin/bash --login
#SBATCH -t 0-6
#SBATCH -p multicore_small
#SBATCH -n 15
#SBATCH -J NDOWN-UK-%%JOBID%%

module load apps/gcc/wrf/4.5

CWD=%%WRFDIR%%

WORK_NAME='UK_NDOWN_3km'
REAL_NAME='UK_REAL_45km'
WRF_NAME='UK_WRF_45km'


WORK_PATH=${CWD}/${WORK_NAME}
REAL_PATH=${CWD}/${REAL_NAME}
WRF_PATH=${CWD}/${WRF_NAME}

cd ${WORK_PATH}

# link the d03 input files, renaming to d02
ln -s ${REAL_PATH}/wrfinput_d03 wrfndi_d02
ln -s ${REAL_PATH}/wrflowinp_d03 wrflowinp_d02

# link the d02 wrfout files, renaming to d01
cd $WRF_PATH
wrfout_input_list=$(ls -1 wrfout_d02*)
cd $WORK_PATH

for wrfout in ${wrfout_input_list[@]}; do
    wrfout_rename=$(echo $wrfout | sed -r "s~d02~d01~g")
    ln -s $WRF_PATH/$wrfout $WORK_PATH/$wrfout_rename
done

time mpirun -np 15 ndown.exe

