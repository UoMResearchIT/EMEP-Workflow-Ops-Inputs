# SPDX-FileCopyrightText: 2025 University of Manchester
#
# SPDX-License-Identifier: apache-2.0

import xarray as xr
from wrf import getvar, to_np, latlon_coords
import netCDF4 as nc
import argparse
from datetime import date, timedelta, datetime
import os
import numpy as np

def get_constants() -> None:
    """
    Set up global dictionaries for command-line argument help texts and PMFINE_GROUP molecular weights.
    Globals:
        arguments (dict): Maps CLI argument names to help strings.
        pmfine_mw (dict): Maps PMFINE_GROUP variable names (and NO3_c) to their molecular weights.
        kg_air_per_mol (float): Mean molecular weight of dry air in kg/mol.
        air_density (float): Air density at 1 atm and 298K (kg/m3).
        pm_coarse_fraction (float): Fraction of coarse NO3_c included in PM2.5.
        g_to_kg_dividing_factor (float): Factor to convert grams to kilograms.
        kg_to_ug_multiplying_factor (float): Factor to convert kilograms to micrograms.
        time_units (str): Time units for NetCDF output.
        time_calendar (str): Calendar type for NetCDF output.
        colon (str): Safe colon character for filenames (":" or "&#x3a;" on Windows).
    Returns:
        None
    """
    global arguments, pmfine_mw, kg_air_per_mol, air_density, pm_coarse_fraction, g_to_kg_dividing_factor, kg_to_ug_multiplying_factor, time_units, time_calendar, colon

    arguments = {
        "--startyear": "Data Start Year",
        "--startmonth": "Data Start Month",
        "--startday": "Data Start Day",
        "--endyear": "Data End Year",
        "--endmonth": "Data End Month",
        "--endday": "Data End Day",
        "--wrfdir": "WRF data directory",
        "--emepdir": "EMEP data directory",
        "--outdir": "Output data directory",
        "--wrfdomain" : "WRF domain"
    }

    pmfine_mw = {
        "SO4": 96, "NO3_f": 62, "NH4_f": 18, "EC_f_wood_new": 12, "EC_f_wood_age": 12,
        "EC_f_ffuel_new": 12, "EC_f_ffuel_age": 12, "pSO4f": 96, "remPPM25": 12, "OM25_p": 1,
        "VBS_TEST": 1, "Ash_f": 12, "ffire_BC": 12, "ffire_remPPM25": 12, "SeaSalt_f": 58,
        "Dust_road_f": 200, "Dust_wb_f": 200, "Dust_sah_f": 200, "NO3_c": 62
    }

    kg_air_per_mol = 0.0289647
    air_density = 1.1845
    pm_coarse_fraction = 0.27
    g_to_kg_dividing_factor = 1000.0
    kg_to_ug_multiplying_factor = 1e9
    time_units = "hours since 1970-01-01 00:00:00"
    time_calendar = "standard"

    if os.name == "nt":
        colon = "&#x3a;"
    else:
        colon = ":"

def get_latlon_shape(ds: nc.Dataset) -> tuple:
    """
    Extract latitude, longitude, and grid shape information from a WRF dataset.
    Args:
        ds: netCDF4.Dataset or similar WRF dataset object.
    Returns:
        tuple: (lat, lon, south_north, west_east, bottom_top)
            - lat: 2D array of latitudes
            - lon: 2D array of longitudes
            - south_north: int, number of grid points in south-north direction
            - west_east: int, number of grid points in west-east direction
            - bottom_top: int, number of vertical levels
    """
    pressureSample = getvar(ds, "pressure", timeidx=0)
    lat, lon = latlon_coords(pressureSample)
    
    south_north = pressureSample.sizes['south_north']
    west_east = pressureSample.sizes['west_east']
    bottom_top = pressureSample.sizes['bottom_top']

    return(lat, lon, south_north, west_east, bottom_top)

def calculate_time_array(wrfDS, emepDS):
    wrf_times_raw = wrfDS.variables["Times"][:]
    emep_times_raw = emepDS.variables["time"][:]

    wrf_times = [b"".join(t).decode("utf-8") if hasattr(t[0], 'decode') else "".join(t) for t in wrf_times_raw]
    wrf_times_dt = [datetime.strptime(t, "%Y-%m-%d_%H:%M:%S") for t in wrf_times]

    emep_time_units = emepDS.variables["time"].units
    emep_times_dt = nc.num2date(emep_times_raw, emep_time_units)
    emep_times_dt_as_datetime = [datetime(t.year, t.month, t.day, t.hour, t.minute, t.second) for t in emep_times_dt]

    common_times = sorted(set(wrf_times_dt) & set(emep_times_dt_as_datetime))

    wrf_indices = [wrf_times_dt.index(t) for t in common_times]
    emep_indices = [emep_times_dt_as_datetime.index(t) for t in common_times]

    return wrf_indices, emep_indices, common_times

def load_3d_wrf_data(ds: nc.Dataset, t: int, common_index: int, varName: str, outArray: np.ndarray) -> None:
    """
    Load a 3D WRF variable for a specific time index into an output array.
    Args:
        ds (netCDF4.Dataset): WRF dataset object.
        t (int): Time index.
        common_index (int): Common index for output array.
        varName (str): Name of the variable to extract.
        outArray (np.ndarray): Output array to store the data.
    Returns:
        None
    """
    varData = getvar(ds, varName, timeidx=t)
    outArray[common_index, :, :] = to_np(varData)

def load_3d_wrf_data_uv(ds: nc.Dataset, t: int, common_index: int, varName: str, outArray: np.ndarray, element_index: int) -> None:
    """
    Load a 3D WRF wind variable for a specific time index into an output array.
    Args:
        ds (netCDF4.Dataset): WRF dataset object.
        t (int): Time index.
        common_index (int): Common index for output array.
        varName (str): Name of the variable to extract.
        outArray (np.ndarray): Output array to store the data.
        element_index (int): Specifies index to choose between u/v or speed/direction.
    Returns:
        None
    """
    varData = getvar(ds, varName, timeidx=t)
    outArray[common_index, :, :] = to_np(varData[element_index, :, :])

def load_4d_wrf_data(ds: nc.Dataset, t: int, common_index: int, varName: str, outArray: np.ndarray) -> None:
    """
    Load a 4D WRF variable for a specific time index into an output array.
    Args:
        ds (netCDF4.Dataset): WRF dataset object.
        t (int): Time index.
        common_index (int): Common index for output array.
        varName (str): Name of the variable to extract.
        outArray (np.ndarray): Output array to store the data.
    Returns:
        None
    """
    varData = getvar(ds, varName, timeidx=t)
    outArray[common_index, :, :, :] = to_np(varData)

def load_4d_wrf_data_uv(ds: nc.Dataset, t: int, common_index: int, varName: str, outArray: np.ndarray, element_index: int) -> None:
    """
    Load a 4D WRF wind variable for a specific time index into an output array.
    Args:
        ds (netCDF4.Dataset): WRF dataset object.
        t (int): Time index.
        common_index (int): Common index for output array.
        varName (str): Name of the variable to extract.
        outArray (np.ndarray): Output array to store the data.
        element_index (int): Specifies index to choose between u/v or speed/direction.
    Returns:
        None
    """
    varData = getvar(ds, varName, timeidx=t)
    outArray[common_index, :, :, :] = to_np(varData[element_index, :, :, :])

def load_4d_emep_data(ds: nc.Dataset, t: int, common_index: int, varName: str, outArray: np.ndarray) -> None:
    """
    Load a 4D EMEP variable for a specific time index into an output array.
    Args:
        ds (netCDF4.Dataset): EMEP dataset object.
        t (int): Time index.
        common_index (int): Common index for output array.
        varName (str): Name of the variable to extract.
        outArray (np.ndarray): Output array to store the data.
    Returns:
        None
    """
    varData = ds[varName][t, :, :, :]
    outArray[common_index, :, :, :] = to_np(varData)[::-1, :, :]

def load_4d_emep_nox(ds: nc.Dataset, t: int, common_index: int, outArray: np.ndarray) -> None:
    """
    Load and sum NO and NO2 from EMEP data to produce total NOX for a specific time index.
    NOX is calculated as:
        NOX = NO + NO2
    Args:
        ds (netCDF4.Dataset): EMEP dataset object.
        t (int): Time index.
        common_index (int): Common index for output array.
        outArray (np.ndarray): Output array to store the NOX data.
    Returns:
        None
    """
    no = ds["NO"][t, :, :, :]
    no2 = ds["NO2"][t, :, :, :]
    outArray[common_index, :, :, :] = (to_np(no) + to_np(no2))[::-1, :, :]

def load_4d_emep_pm25(ds: nc.Dataset, t: int, common_index: int, outArray: np.ndarray) -> None:
    """
    Calculate and load PM2.5 mass concentration from EMEP species for a specific time index into an output array.
    For each species, the conversion from mol/mol to kg/kg is performed as:
        Y = X * (MWspec / MWair)
    where:
        Y: mass fraction (kg/kg)
        X: mixing ratio (mol/mol)
        MWspec: molecular weight of the species (kg/mol)
        MWair: mean molecular weight of dry air (kg/mol)
    The final PM2.5 is then converted to micrograms per cubic meter (ug/m3).
    Args:
        ds (netCDF4.Dataset): EMEP dataset object.
        t (int): Time index.
        common_index (int): Common index for output array.
        outArray (np.ndarray): Output array to store the PM2.5 data.
    Returns:
        None
    """
    pm25 = np.zeros_like(ds["SO4"][t, :, :, :])

    for key, val in pmfine_mw.items():
        mw = val / g_to_kg_dividing_factor

        if key == "NO3_c":
            pm25 += pm_coarse_fraction * ds[key][t, :, :, :] * (mw / kg_air_per_mol)
        else:
            pm25 += ds[key][t, :, :, :] * (mw / kg_air_per_mol)

    pm25_ugm3 = convert_pm_mixing_to_ugm3(pm25, air_density)
    outArray[common_index, :, :, :] = to_np(pm25_ugm3)[::-1, :, :]

def convert_pm_mixing_to_ugm3(pm_mixing: np.ndarray, air_density: float) -> np.ndarray:
    """
    Convert particulate matter mixing ratio from kg/kg to micrograms per cubic meter (ug/m3).
    The conversion performed is:
        kg/kg * kg/m3 * 1e9 -> ug/m3
    Args:
        pm_mixing (np.ndarray): Particulate matter mixing ratio in kg/kg.
        air_density (float): Air density in kg/m3.
    Returns:
        np.ndarray: Particulate matter concentration in ug/m3.
    """
    return pm_mixing * air_density * kg_to_ug_multiplying_factor

def data_extract(wrfDir, emepDir, outputDir, wrfFile, emepFile, outFile):
    """
    Extracts and collates data from WRF and EMEP NetCDF files, and writes selected variables to a new NetCDF output file.
    Args:
        wrfDir (str): Directory containing WRF input files.
        emepDir (str): Directory containing EMEP input files.
        outputDir (str): Directory to write the output file.
        wrfFile (str): Filename of the WRF input file.
        emepFile (str): Filename of the EMEP input file.
        outFile (str): Filename for the output NetCDF file.
    Returns:
        None
    """
    wrfDS = nc.Dataset(os.path.join(wrfDir, wrfFile))
    emepDS = nc.Dataset(os.path.join(emepDir, emepFile))
      
    lat, lon, south_north, west_east, bottom_top = get_latlon_shape(wrfDS)
    wrf_indices, emep_indices, common_times = calculate_time_array(wrfDS, emepDS)

    common_times_num = nc.date2num(common_times, units=time_units, calendar=time_calendar)

    with nc.Dataset(os.path.join(outputDir, outFile), "w", format="NETCDF4") as out:
        out.createDimension("Time", None)
        out.createDimension("south_north", south_north)
        out.createDimension("west_east", west_east)
        out.createDimension("bottom_top", bottom_top)
        
        out.createVariable("XLAT", "f4", ("south_north", "west_east"))[:] = to_np(lat)
        out.createVariable("XLONG", "f4", ("south_north", "west_east"))[:] = to_np(lon)

        time_var = out.createVariable("TIME", "f4", ("Time",))
        time_var[:] = common_times_num
        time_var.units = time_units
        time_var.calendar = time_calendar

        umet_var = out.createVariable("UMET", "f4", ("Time", "bottom_top", "south_north", "west_east"))
        umet10_var = out.createVariable("UMET10", "f4", ("Time", "south_north", "west_east"))
        uvmet_wspd_var = out.createVariable("UVMET WSPD", "f4", ("Time", "bottom_top", "south_north", "west_east"))
        uvmet10_wspd_var = out.createVariable("UVMET 10 WSPD", "f4", ("Time", "south_north", "west_east"))
        vmet_var = out.createVariable("VMET", "f4", ("Time", "bottom_top", "south_north", "west_east"))
        vmet10_var = out.createVariable("VMET10", "f4", ("Time", "south_north", "west_east"))
        uvmet_wdir_var = out.createVariable("UVMET WDIR", "f4", ("Time", "bottom_top", "south_north", "west_east"))
        uvmet10_wdir_var = out.createVariable("UVMET 10 WDIR", "f4", ("Time", "south_north", "west_east"))

        t2_var  = out.createVariable("T2",  "f4", ("Time", "south_north", "west_east"))
        t_var  = out.createVariable("T",   "f4", ("Time", "bottom_top", "south_north", "west_east"))
        tcwv_var = out.createVariable("Precipitable Water", "f4", ("Time", "south_north", "west_east"))
        maxref_var = out.createVariable("MAXREF", "f4", ("Time", "south_north", "west_east"))
        geopot_var = out.createVariable("Geopotential Height", "f4", ("Time", "bottom_top", "south_north", "west_east"))

        o3_var  = out.createVariable("O3", "f4", ("Time", "bottom_top", "south_north", "west_east"))
        nox_var = out.createVariable("NOX", "f4", ("Time", "bottom_top", "south_north", "west_east"))
        pm25_var = out.createVariable("PM25_TOT", "f4", ("Time", "bottom_top", "south_north", "west_east")) 

        for wrf_idx, emep_idx, time_val, common_index in zip(wrf_indices, emep_indices, common_times, range(len(common_times))): # The following descriptions are from https://wrf-python.readthedocs.io/en/latest/diagnostics.html
            load_3d_wrf_data(wrfDS, wrf_idx, common_index, "T2", t2_var)
            load_3d_wrf_data(wrfDS, wrf_idx, common_index, "pw", tcwv_var) # Precipitable Water in kg/m2
            load_3d_wrf_data(wrfDS, wrf_idx, common_index, "mdbz", maxref_var) # Maximum Simulated Radar Reflectivity in dBZ

            load_4d_wrf_data(wrfDS, wrf_idx, common_index, "tk", t_var) # Temperature in Kelvin
            load_4d_wrf_data(wrfDS, wrf_idx, common_index, "height", geopot_var) # Model Height for Mass Grid (from Mean Sea Level) in m by default

            load_4d_wrf_data_uv(wrfDS, wrf_idx, common_index, "uvmet", umet_var, 0) # U Component of Wind Rotated to Earth Coordinates (in m/s by default)
            load_3d_wrf_data_uv(wrfDS, wrf_idx, common_index, "uvmet10", umet10_var, 0) # 10m U Component of Wind Rotated to Earth Coordinates (in m/s by default)
            load_4d_wrf_data_uv(wrfDS, wrf_idx, common_index, "uvmet_wspd_wdir", uvmet_wspd_var, 0) # Wind Speed Rotated to Earth Coordinates (in m/s by default)
            load_3d_wrf_data_uv(wrfDS, wrf_idx, common_index, "uvmet10_wspd_wdir", uvmet10_wspd_var, 0) # 10m Wind Speed Rotated to Earth Coordinates (in m/s by default)
            load_4d_wrf_data_uv(wrfDS, wrf_idx, common_index, "uvmet", vmet_var, 1) # V Component of Wind Rotated to Earth Coordinates (in m/s by default)
            load_3d_wrf_data_uv(wrfDS, wrf_idx, common_index, "uvmet10", vmet10_var, 1) # 10m V Component of Wind Rotated to Earth Coordinates (in m/s by default)
            load_4d_wrf_data_uv(wrfDS, wrf_idx, common_index, "uvmet_wspd_wdir", uvmet_wdir_var, 1) # Wind Direction Rotated to Earth Coordinates (in m/s by default)
            load_3d_wrf_data_uv(wrfDS, wrf_idx, common_index, "uvmet10_wspd_wdir", uvmet10_wdir_var, 1) # 10m Wind Direction Rotated to Earth Coordinates (in m/s by default)
            
            load_4d_emep_data(emepDS, emep_idx, common_index, "O3", o3_var)
            load_4d_emep_nox(emepDS, emep_idx, common_index, nox_var)
            load_4d_emep_pm25(emepDS, emep_idx, common_index, pm25_var)

def parse_cli_arguments() -> dict:
    """
    Parse command-line arguments for WRF/EMEP data extraction.
    Returns:
        dict: Dictionary mapping argument names to their parsed values.
    """
    parser = argparse.ArgumentParser(description="WRF/EMEP Data Extraction and Collation")

    for arg, help_text in arguments.items():
        condition = "year" in arg or "month" in arg or "day" in arg

        if arg == "--wrfdomain":
            parser.add_argument(arg, required=False, help=help_text, default="d01")
        else:
            parser.add_argument(arg, required=True, help=help_text, type=int if condition else str)    

    return vars(parser.parse_args())

def main() -> None:
    """
    Main entry point for the WRF/EMEP data extraction workflow.
    - Initializes global constants.
    - Parses command-line arguments.
    - Iterates over the specified date range, constructing filenames and calling data extraction for each day.
    Returns:
        None
    """
    print('Getting Arguments...')
    
    get_constants()
    args = parse_cli_arguments()

    startYear, startMonth, startDay = args["startyear"], args["startmonth"], args["startday"]
    endYear, endMonth, endDay = args["endyear"], args["endmonth"], args["endday"]
    wrfDir, emepDir, outputDir = args["wrfdir"], args["emepdir"], args["outdir"]
    wrfdom = args["wrfdomain"]

    currentDate = date(startYear, startMonth, startDay)
    endDate = date(endYear, endMonth, endDay)

    print('Starting Data Extraction...')
    
    while (currentDate <= endDate):
        currentYear = currentDate.year
        currentMonth = currentDate.month
        currentDay = currentDate.day
        
        wrfFile = f"wrfout_{wrfdom}_{currentYear:02d}-{currentMonth:02d}-{currentDay:02d}_00{colon}00{colon}00"
        emepFile = f"EMEP_OUT_{currentYear:02d}{currentMonth:02d}{currentDay:02d}.nc"
        outFile = f"WRF_EMEP_{currentYear:02d}{currentMonth:02d}{currentDay:02d}.nc"
        
        data_extract(wrfDir, emepDir, outputDir, wrfFile, emepFile, outFile)
        
        currentDate += timedelta(days=1)
    
    print('Finished Data Extraction!')

if __name__ == "__main__":
    main()
