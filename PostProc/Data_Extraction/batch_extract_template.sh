#!/bin/bash --login

# SPDX-FileCopyrightText: 2025 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

#SBATCH -t 0-6
#SBATCH -p serial
#SBATCH -J DATA-%%DOM%%-%%JOBID%%

source ~/bin/conda_activate.sh 
conda activate wrf-python

CWD=%%POSTPROCDIR%%

STARTYEAR=%%YRST%%
STARTMONTH=%%MONST%%
STARTDAY=%%DAYST%%

ENDYEAR=%%YREND%%
ENDMONTH=%%MONEND%%
ENDDAY=%%DAYEND%%

WRFDIR=%%WRFDIR%%
EMEPDIR=%%EMEPDIR%%
OUTPUTDIR=%%OUTDIR%%


python data_extraction.py --startyear $STARTYEAR --startmonth $STARTMONTH --startday $STARTDAY \
						--endyear $ENDYEAR --endmonth $ENDMONTH --endday $ENDDAY \
						--wrfdir $WRFDIR --emepdir $EMEPDIR --outdir $OUTPUTDIR
