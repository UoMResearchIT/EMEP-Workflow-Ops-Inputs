# SPDX-FileCopyrightText: 2025 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

import xarray as xr
from wrf import getvar, to_np, latlon_coords
import netCDF4 as nc
import argparse
from datetime import date, timedelta
from os import path
import numpy as np

def get_latlon_shape(ds):
   pressureSample = getvar(ds, "pressure", timeidx=0)
   lat, lon = latlon_coords(pressureSample)
   south_north = pressureSample.sizes['south_north']
   west_east = pressureSample.sizes['west_east']
   bottom_top = pressureSample.sizes['bottom_top']
   return(lat, lon, south_north, west_east, bottom_top)

def load_3d_wrf_data(ds, t, varName, outArray):
    varData = getvar(ds, varName, timeidx=t)
    outArray[t, :, :] = to_np(varData)

def load_4d_wrf_data(ds, t, varName, outArray):
    varData = getvar(ds, varName, timeidx=t)
    outArray[t, :, :, :] = to_np(varData)

def load_4d_emep_data(ds, t, varName, outArray):
    varData = ds[varName][t, :, :, :]
    outArray[t, :, :, :] = to_np(varData)

def load_4d_emep_nox(ds, t, outArray):
    no = ds["NO"][t, :, :, :]
    no2 = ds["NO2"][t, :, :, :]
    outArray[t, :, :, :] = to_np(no) + to_np(no2) # NOX = NO + NO2

def load_4d_emep_pm25(ds, t, outArray):
    kg_air_per_mol = 0.0289647  # mean molecular weight of dry air in kg/mol
    air_density = 1.1845 # at 1 atm and 298K (kg/m3)

    pmfine_vars = [
        "SO4", "NO3_f", "NH4_f", "EC_f_wood_new", "EC_f_wood_age",
        "EC_f_ffuel_new", "EC_f_ffuel_age", "pSO4f", "remPPM25", "OM25_p",
        "VBS_TEST", "Ash_f", "ffire_BC", "ffire_remPPM25", "SeaSalt_f",
        "Dust_road_f", "Dust_wb_f", "Dust_sah_f"
    ]

    pmfine_mw = {
        "SO4": 96, "NO3_f": 62, "NH4_f": 18, "EC_f_wood_new": 12, "EC_f_wood_age": 12,
        "EC_f_ffuel_new": 12, "EC_f_ffuel_age": 12, "pSO4f": 96, "remPPM25": 12, "OM25_p": 1,
        "VBS_TEST": 1, "Ash_f": 12, "ffire_BC": 12, "ffire_remPPM25": 12, "SeaSalt_f": 58,
        "Dust_road_f": 200, "Dust_wb_f": 200, "Dust_sah_f": 200, "NO3_c": 62
    }
    
    # Y = X * (MWspec / MWair)
    # Y: mass fraction (kg/kg), X: mix ratio (mol/mol), MW: molecular weight (kg/mol)

    pm25 = np.zeros_like(ds["SO4"][t, :, :, :])
    for var in pmfine_vars:
        mw = pmfine_mw[var] / 1000.0
        pm25 += ds[var][t, :, :, :] * (mw / kg_air_per_mol)

    mw_no3c = pmfine_mw["NO3_c"] / 1000.0
    pm25 += 0.27 * ds["NO3_c"][t, :, :, :] * (mw_no3c / kg_air_per_mol)
    pm25_ugm3 = convert_pm_mixing_to_ugm3(pm25, air_density)
    outArray[t, :, :, :] = to_np(pm25_ugm3)

def convert_pm_mixing_to_ugm3(pm_mixing, air_density):
    # kg/kg * kg/m3 * 1e9 -> ug/m3
    return pm_mixing * air_density * 1e9
    
    
def data_extract(wrfDir, emepDir, outputDir, wrfFile, emepFile, outFile):
   
   wrfDS = nc.Dataset(path.join(wrfDir, wrfFile))
   emepDS = nc.Dataset(path.join(emepDir, emepFile))
      
   ntimes = wrfDS.dimensions["Time"]
   
   lat, lon, south_north, west_east, bottom_top = get_latlon_shape(wrfDS)

   with nc.Dataset(path.join(outputDir, outFile), "w", format="NETCDF4") as out:
        out.createDimension("Time", None)
        out.createDimension("south_north", south_north)
        out.createDimension("west_east", west_east)
        out.createDimension("bottom_top", bottom_top)
        
        out.createVariable("XLAT", "f4", ("south_north", "west_east"))[:] = to_np(lat)
        out.createVariable("XLONG", "f4", ("south_north", "west_east"))[:] = to_np(lon)

        u10_var = out.createVariable("U10", "f4", ("Time", "south_north", "west_east"))
        v10_var = out.createVariable("V10", "f4", ("Time", "south_north", "west_east"))
        t2_var  = out.createVariable("T2",  "f4", ("Time", "south_north", "west_east"))
        ua_var  = out.createVariable("U",   "f4", ("Time", "bottom_top", "south_north", "west_east"))
        va_var  = out.createVariable("V",   "f4", ("Time", "bottom_top", "south_north", "west_east"))
        t_var  = out.createVariable("T",   "f4", ("Time", "bottom_top", "south_north", "west_east"))

        o3_var  = out.createVariable("O3", "f4", ("Time", "bottom_top", "south_north", "west_east"))
        nox_var = out.createVariable("NOX", "f4", ("Time", "bottom_top", "south_north", "west_east"))
        pm25_var = out.createVariable("PM25_TOT", "f4", ("Time", "bottom_top", "south_north", "west_east"))

        tcwv_var = out.createVariable("TCWV", "f4", ("Time", "south_north", "west_east"))
        maxref_var = out.createVariable("MAXREF", "f4", ("Time", "south_north", "west_east"))
        geopot_var = out.createVariable("Geopotential", "f4", ("Time", "bottom_top", "south_north", "west_east")) 

        for t in range(ntimes.size): # 1 iter
            load_3d_wrf_data(wrfDS, t, "U10", u10_var)
            load_3d_wrf_data(wrfDS, t, "V10", v10_var)
            load_3d_wrf_data(wrfDS, t, "T2", t2_var)
            load_3d_wrf_data(wrfDS, t, "pw", tcwv_var)
            load_3d_wrf_data(wrfDS, t, "mdbz", maxref_var)

            load_4d_wrf_data(wrfDS, t, "ua", ua_var)
            load_4d_wrf_data(wrfDS, t, "va", va_var)
            load_4d_wrf_data(wrfDS, t, "T", t_var)
            load_4d_wrf_data(wrfDS, t, "geopt", geopot_var)
            
            load_4d_emep_data(emepDS, t, "O3", o3_var)
            load_4d_emep_nox(emepDS, t, nox_var)
            load_4d_emep_pm25(emepDS, t, pm25_var)

def parse_cli_arguments():
    parser = argparse.ArgumentParser(description="WRF/EMEP Data Extraction and Collation")
    
    parser.add_argument("--startyear", required=True, help="Data Start Year")
    parser.add_argument("--startmonth", required=True, help="Data Start Month")
    parser.add_argument("--startday", required=True, help="Data Start Day")

    parser.add_argument("--endyear", required=True, help="Data End Year")
    parser.add_argument("--endmonth", required=True, help="Data End Month")
    parser.add_argument("--endday", required=True, help="Data End Day")
    
    parser.add_argument("--wrfdir", required=True, help="WRF data directory")
    parser.add_argument("--emepdir", required=True, help="EMEP data directory")
    parser.add_argument("--outdir", required=True, help="Output data directory")

    parser.add_argument("--wrfdomain", required=False, default="d01", help="WRF domain")

    return vars(parser.parse_args())
    

def main():
    print('get arguments')
    
    args = parse_cli_arguments()

    startYear = int(args["startyear"])
    startMonth = int(args["startmonth"])
    startDay = int(args["startday"])
    currentDate = date(startYear, startMonth, startDay)

    endYear = int(args["endyear"])
    endMonth = int(args["endmonth"])
    endDay = int(args["endday"])
    endDate = date(endYear, endMonth, endDay)
    
    wrfDir = args["wrfdir"]
    emepDir = args["emepdir"]
    outputDir = args["outdir"]

    wrfdom = args["wrfdomain"]

    
    print('start data extraction')
    
    
    while (currentDate <= endDate):
    
        currentYear = currentDate.year
        currentMonth = currentDate.month
        currentDay = currentDate.day
        
        wrfFile = f"wrfout_{wrfdom}_{currentYear:02d}-{currentMonth:02d}-{currentDay:02d}_00&#x3a;00&#x3a;00" # colons not allowed by windows filesystem 
        emepFile = f"EMEP_OUT_{currentYear:02d}{currentMonth:02d}{currentDay:02d}.nc"
        
        outFile = f"WRF_EMEP_{currentYear:02d}{currentMonth:02d}{currentDay:02d}.nc"
        
        data_extract(wrfDir, emepDir, outputDir, wrfFile, emepFile, outFile)
        
        currentDate = currentDate + timedelta(days=1)
    
    print('finished data extraction')


if __name__ == "__main__":
    main()
