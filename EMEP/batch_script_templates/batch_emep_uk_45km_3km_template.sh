#!/bin/bash --login

# SPDX-FileCopyrightText: 2025 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

#SBATCH -t 1-0
#SBATCH -p hpcpool
#SBATCH -A hpc-dt-targ
#SBATCH -N 4
#SBATCH -n 128
#SBATCH -J EMEP-UK-%%JOBID%%

module load compilers/gcc/8.2.0
module load libs/gcc/netcdf/4.9.2
module load mpi/gcc/openmpi/4.1.8-gcc-8.2.0

CWD=%%EMEPDIR%%
WRF_DIR=%%WRFDIR%%


WRF_45KM_NAME='UK_WRF_45km'
WRF_3KM_NAME='UK_3km'
MET_45KM_NAME='wrf_meteo/UK_45km_grid'
MET_3KM_NAME='wrf_meteo/UK_3km_grid'
WORK_NAME_45KM='UK_45km_domain'
WORK_NAME_3KM='UK_3km_domain'


WORK_PATH_45KM=${CWD}/${WORK_NAME_45KM}
WORK_PATH_3KM=${CWD}/${WORK_NAME_3KM}
MET_45KM_PATH=${CWD}/${MET_45KM_NAME}
MET_3KM_PATH=${CWD}/${MET_3KM_NAME}
WRF_45KM_PATH=${WRF_DIR}/${WRF_45KM_NAME}
WRF_3KM_PATH=${WRF_DIR}/${WRF_3KM_NAME}

### EMEP executable
EMEP_EXEC=%%EMEPEXEC%%


### function for linking WRF output files in an EMEP friendly manner
link_met_data () {
	file_list=$(ls -1 $1/wrfout*)

	for FILE in ${file_list[@]};
	do
		parts=(${FILE//// })              # split FILE string on the / delimiter
		filename=${parts[${#parts[@]}-1]} # select the last value, which is the filename
		fileparts=(${filename//:/ })      # split the filename string on the : delimiter
		LOCAL_FILE=${fileparts[0]}        # select the first value as our local filename
		ln -s $FILE $LOCAL_FILE  
	done
}


### operational code

# create the met file links
cd ${MET_45KM_PATH}
link_met_data ${WRF_45KM_PATH}
cd ${MET_3KM_PATH}
link_met_data ${WRF_3KM_PATH}

# run EMEP for 45km UK grid
cd ${WORK_PATH_45KM}
mpiexec --mca -np 128 ${EMEP_EXEC}

# run EMEP for 3km UK grid
cd ${WORK_PATH_3KM}
mpiexec --mca -np 128 ${EMEP_EXEC}

