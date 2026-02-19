#!/bin/bash --login

# SPDX-FileCopyrightText: 2025 - 2026 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

#SBATCH -t 0-6
#SBATCH -p serial
#SBATCH -J DATA-%%DOM%%-%%JOBID%%

source ~/bin/conda_activate.sh 
conda activate wrf-python

CWD=%%POSTPROCDIR%%

WRFDIR=%%WRFDIR%%
EMEPDIR=%%EMEPDIR%%
OUTPUTDIR=%%OUTDIR%%

STARTYEAR=%%YRST%%
STARTMONTH=%%MONST%%
STARTDAY=%%DAYST%%

ENDYEAR=%%YREND%%
ENDMONTH=%%MONEND%%
ENDDAY=%%DAYEND%%

start_sec=$(date -d "${STARTYEAR}-${STARTMONTH}-${STARTDAY}" +%s)
end_sec=$(date -d "${ENDYEAR}-${ENDMONTH}-${ENDDAY}" +%s)

current_sec=$start_sec

while (( current_sec <= end_sec )); do
	YEAR=$(date -d "@$current_sec" +%Y)
	MONTH=$(date -d "@$current_sec" +%m)
	DAY=$(date -d "@$current_sec" +%d)
	python data_extraction.py --startyear $YEAR --startmonth $MONTH --startday $DAY \
                                  --endyear $YEAR --endmonth $MONTH --endday $DAY \
                                  --wrfdir $WRFDIR --emepdir $EMEPDIR --outdir $OUTPUTDIR
	current_sec=$(( current_sec + 86400 ))
done
