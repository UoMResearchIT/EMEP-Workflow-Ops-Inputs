# SPDX-FileCopyrightText: 2025 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

import xarray as xr
from wrf import getvar, to_np, latlon_coords
import netCDF4 as nc
import argparse
from datetime import date, timedelta
from os import path

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

#def load_4d_emep_PM25_data(ds, t, outArray):
    
    
def data_extract(wrfDir, emepDir, outputDir, wrfFile, emepFile, outFile):
   
   wrfDS = nc.Dataset(path.join(wrfDir, wrfFile))
   emepDS = nc.Dataset(path.join(emepDir, emepFile))
      
   ntimes = wrfDS.dimensions["Time"]
   
   lat, lon, south_north, west_east, bottom_top = get_latlon_shape(wrfDS)

   with nc.Dataset(outputDir+outFile, "w", format="NETCDF4") as out:
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

        o3_var  = out.createVariable("O3", "f4", ("Time", "bottom_top", "south_north", "west_east")) 

        for t in range(ntimes.size):
            load_3d_wrf_data(wrfDS, t, "U10", u10_var)
            load_3d_wrf_data(wrfDS, t, "V10", v10_var)
            load_3d_wrf_data(wrfDS, t, "T2", t2_var)

            load_4d_wrf_data(wrfDS, t, "ua", ua_var)
            load_4d_wrf_data(wrfDS, t, "va", va_var)
            
            load_4d_emep_data(emepDS, t, "O3", o3_var)


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
        
        wrfFile = f"wrfout_{wrfdom}_{currentYear:02d}-{currentMonth:02d}-{currentDay:02d}_00:00:00"
        emepFile = f"EMEP_OUT_{currentYear:02d}{currentMonth:02d}{currentDay:02d}.nc"
        
        outFile = f"WRF_EMEP_{currentYear:02d}{currentMonth:02d}{currentDay:02d}.nc"
        
        data_extract(wrfDir, emepDir, outputDir, wrfFile, emepFile, outFile)
        
        currentDate = currentDate + timedelta(days=1)
    
    print('finished data extraction')


if __name__ == "__main__":
    main()
