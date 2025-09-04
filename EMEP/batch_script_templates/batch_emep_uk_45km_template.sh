#!/bin/bash --login
#SBATCH -t 1-0
#SBATCH -p multicore
#SBATCH -n 36
#SBATCH -J EMEP-UK45-%%JOBID%%

module load compilers/gcc/8.2.0
module load libs/gcc/netcdf/4.9.2
module load mpi/gcc/openmpi/4.1.8-gcc-8.2.0

CWD=%%EMEPDIR%%
WRF_DIR=%%WRFDIR%%


WRF_45KM_NAME='UK_WRF_45km'
MET_45KM_NAME='wrf_meteo/UK_45km_grid'
WORK_NAME_45KM='UK_45km_domain'


WORK_PATH_45KM=${CWD}/${WORK_NAME_45KM}
MET_45KM_PATH=${CWD}/${MET_45KM_NAME}
WRF_45KM_PATH=${WRF_DIR}/${WRF_45KM_NAME}

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

# run EMEP for 45km UK grid
cd ${WORK_PATH_45KM}
mpiexec --mca -np 36 ${EMEP_EXEC}


