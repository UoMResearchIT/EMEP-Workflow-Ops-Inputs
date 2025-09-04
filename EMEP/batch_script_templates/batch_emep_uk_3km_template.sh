#!/bin/bash --login
#SBATCH -t 1-0
#SBATCH -p hpcpool
#SBATCH -A hpc-dt-targ
#SBATCH -N 4
#SBATCH -n 128
#SBATCH -J EMEP-UK3-%%JOBID%%

module load compilers/gcc/8.2.0
module load libs/gcc/netcdf/4.9.2
module load mpi/gcc/openmpi/4.1.8-gcc-8.2.0

CWD=%%EMEPDIR%%
WRF_DIR=%%WRFDIR%%


WRF_3KM_NAME='UK_3km'
MET_3KM_NAME='wrf_meteo/UK_3km_grid'
WORK_NAME_3KM='UK_3km_domain'


WORK_PATH_3KM=${CWD}/${WORK_NAME_3KM}
MET_3KM_PATH=${CWD}/${MET_3KM_NAME}
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
cd ${MET_3KM_PATH}
link_met_data ${WRF_3KM_PATH}

# run EMEP for 3km UK grid
cd ${WORK_PATH_3KM}
mpiexec --mca -np 128 ${EMEP_EXEC}

