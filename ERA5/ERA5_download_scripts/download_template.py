#!/usr/bin/env python

import time
from datetime import date
from datetime import timedelta

import cdsapi

c = cdsapi.Client()


# Set dates for data extraction - SAMBBA campaign period
idate = date(%%YRST%%,%%MONST%%,%%DAYST%%)
edate = date(%%YREND%%,%%MONEND%%,%%DAYEND%%)

while (idate <= edate):

    iyear = idate.year
    imonth = idate.month
    iday = idate.day

    stryear  = "%04d" % (iyear)
    strmonth = "%02d" % (imonth)
    strday   = "%02d" % (iday)
    strdate = "%d%02d%02d" % (iyear, imonth, iday)
    print(strdate)   

    # extract 3D data
    c.retrieve(
        "reanalysis-era5-pressure-levels",
        {
            'product_type': 'reanalysis',
            'data_format': 'grib',
            'download_format': 'unarchived',
            'year': stryear,
            'month': strmonth,
            'day': strday,
            'variable': [
                'geopotential', 'temperature', 'relative_humidity',
                'u_component_of_wind', 'v_component_of_wind',
            ],
            'pressure_level': [
                '30', '50',
                '70', '100', '125',
                '150', '175', '200',
                '225', '250', '300',
                '350', '400', '450',
                '500', '550', '600',
                '650', '700', '750',
                '775', '800', '825',
                '850', '875', '900',
                '925', '950', '975',
                '1000',
            ],
            'time': [
                '00:00', '06:00', '12:00',
                '18:00',
            ],
            'area': [90, -180, 15, 180],
            'grid': [0.5,0.5],
        },
        "preslev_"+strdate+".grib")
    
    # extract surface data
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'format': 'grib',
            'year': stryear,
            'month': strmonth,
            'day': strday,
            'variable': [
                '10m_u_component_of_wind', '10m_v_component_of_wind', '2m_dewpoint_temperature',
                '2m_temperature', 'land_sea_mask', 'mean_sea_level_pressure',
                'sea_ice_cover', 'sea_surface_temperature', 'skin_temperature',
                'snow_density', 'snow_depth', 'soil_temperature_level_1',
                'soil_temperature_level_2', 'soil_temperature_level_3', 'soil_temperature_level_4',
                'surface_pressure', 'volumetric_soil_water_layer_1', 'volumetric_soil_water_layer_2',
                'volumetric_soil_water_layer_3', 'volumetric_soil_water_layer_4',
            ],
            'time': [
                '00:00', '06:00', '12:00',
                '18:00',
            ],
            'area': [90, -180, 15, 180],
        },
        "surface_"+strdate+".grib")
    
        
    # move to next day
    
    idate = idate + timedelta(days=1) 

print("End.")

