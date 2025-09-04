#!/bin/bash --login
#$ -N WPS-%%JOBID%%            
#$ -cwd
#$ -pe smp.pe 8
#$ -hold_jid ERA5-%%JOBID%%
#SBATCH -t 0-6
#SBATCH -p multicore_small
#SBATCH -n 8
#SBATCH -J WPS-%%JOBID%%

module load apps/gcc/wps/4.5

## setting access paths for operations
CWD=%%WPSDIR%%
GRIB_DIR=%%ERA5DIR%%

SFC_PREFIX='surface_'
ATM_PREFIX='preslev_'


### setting paths for working directories
SFC_GRIB_DIR=${CWD}/WPS_UNGRIB_SFC
ATM_GRIB_DIR=${CWD}/WPS_UNGRIB_ATM

EMEP_MET_DIR=${CWD}/WPS_METGRID_50km
UK_MET_DIR=${CWD}/WPS_METGRID_45km


### operational code


## ungrib work, for surface data
cd ${SFC_GRIB_DIR}
# link to data
link_grib.csh ${GRIB_DIR}/${SFC_PREFIX}*
# ungrib surface data
ungrib.exe 2>&1 | tee ungrib.sfc.${MONTH}.log &

## ungrib work, for atmospheric data
cd ${ATM_GRIB_DIR}
# link to data
link_grib.csh ${GRIB_DIR}/${ATM_PREFIX}*
# ungrib surface data
ungrib.exe 2>&1 | tee ungrib.atm.${MONTH}.log &

wait # wait for the two ungrib processes to finish


## metgrid work, 50km EMEP grid
cd ${EMEP_MET_DIR}
# link to the met data
ln -sf ${SFC_GRIB_DIR}/SFCFILE* .
ln -sf ${ATM_GRIB_DIR}/ATMFILE* .
# run metgrid
mpiexec -np 4 metgrid.exe 2>&1 | tee metgrid.${MONTH}.log  &

## metgrid work, 3km EMEP grid
cd ${UK_MET_DIR}
# link to the met data
ln -sf ${SFC_GRIB_DIR}/SFCFILE* .
ln -sf ${ATM_GRIB_DIR}/ATMFILE* .
# run metgrid
mpiexec -np 4 metgrid.exe 2>&1 | tee metgrid.${MONTH}.log  &

wait # wait for the two met grid processes to finish
	
## tidy up once we've finished
cd $CWD
rm ${EMEP_MET_DIR}/SFCFILE* ${EMEP_MET_DIR}/ATMFILE*
rm ${UK_MET_DIR}/SFCFILE* ${UK_MET_DIR}/ATMFILE*
rm ${SFC_GRIB_DIR}/SFCFILE* ${ATM_GRIB_DIR}/ATMFILE*

