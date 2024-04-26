#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ERA5 files downloader for PanguWeather.
"""

import pickle
import cdsapi
import argparse
import pandas as pd
import subprocess
import numpy as np
import os
    
parser = argparse.ArgumentParser(description="Download ERA5 data")

parser.add_argument("--output", "-o",
                    type=str,
                    default="/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/AI-models-input",
                    help="Path to the output folder.")

parser.add_argument("--from-file",
                    action="store_true",
                    help="Dates to download, stored in a csv file.")

parser.add_argument("--path",
                    type=str,
                    default="/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/ERA5/needed_times_LT.csv",
                    help="Path to the csv file containing the dates to download.")

parser.add_argument("--surface","-s",
                    action="store_true",
                    help="Downloading only surface field if present.")

parser.add_argument("--pressure","-p",
                    action="store_true",
                    help="Downloading only pressure-dependant field if present.")

parser.add_argument("--date",
                    type=str,
                    default=False,
                    help = "Date to download, format YYYY or YYYYMM or YYYYMMDD")

parser.add_argument("--time",
                    type=str,
                    default=False,
                    help = "Hour to download, format HH")

parser.add_argument("--test",
                    action="store_true",
                    help="Test the downloader.")

args = parser.parse_args()

folder_path =  args.output

# Choose what dates to download depending on parsed arguments.
if args.from_file:
    dates1 = pd.read_csv(args.path, header = None, index_col=0, parse_dates=True).index
else:
    dates1 = pd.Series()

if args.date:
    year = args.date[:4]
    if len(args.date) == 4:
        if args.time:
            dates = pd.date_range(start = year + "-01-01 " + args.time + ":00", end = year + "-12-31 " + args.time + ":00", freq = "h", tz='utc')
        else:
            dates = pd.date_range(start = year + "-01-01 00:00", end = year + "-12-31 23:00", freq = "h", tz='utc')
            
    elif len(args.date) == 6:
        month = args.date[4:]
        if args.time:
            dates = pd.date_range(start = year + "-" + month + "-01 " + args.time + ":00", end = year + "-" + month + "-31 " + args.time + ":00", freq = "h", tz='utc')
        else:
            dates = pd.date_range(start = year + "-" + month + "-01 00:00", end = year + "-" + month + "-31 23:00", freq = "h", tz='utc')
            
    elif len(args.date) == 8:
        month = args.date[4:6]
        day = args.date[6:]
        if args.time:
            dates = pd.date_range(start = year + "-" + month + "-" + day + " " + args.time + ":00", end = year + "-" + month + "-" + day + " " + args.time + ":00", freq = "h", tz='utc')
        else:
            dates = pd.date_range(start = year + "-" + month + "-" + day + " 00:00", end = year + "-" + month + "-" + day + " 23:00", freq = "h", tz='utc')
    
    else:
        raise ValueError("Date format not recognized.")
    
    if not(dates1.empty):
        dates = dates.intersection(dates1)
    
else:
    if dates1.empty:
        dates = pd.date_range(start = (pd.Timestamp.today() - pd.Timedelta(hours = 24)).strftime("%Y-%m-%d %H"), end = pd.Timestamp.today(), freq = "H")
    else:
        dates = dates1


# Load the dates already downloaded.    
when = pd.read_csv("/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/AI-models-input/when.csv",
                   header = None,
                   index_col=0,
                   parse_dates=True
                   ).index


datas = [('reanalysis-era5-single-levels',
          "surface_variables",
          ['mean_sea_level_pressure', '10m_u_component_of_wind', '10m_v_component_of_wind', '2m_temperature'])]*(args.surface or not(args.surface or args.pressure)) +\
    [('reanalysis-era5-pressure-levels',
      "pressure_variables",
      ['geopotential', 'specific_humidity', 'temperature', 'u_component_of_wind', 'v_component_of_wind'])]*(args.pressure or not(args.surface or args.pressure))

c = cdsapi.Client()

dates_gr = dates.groupby(dates.date)

for date in dates_gr:
    group = dates_gr[date]
    
    try:
        year, month, day = date.strftime("%Y"), date.strftime("%m"), date.strftime("%d")
        
        print("\nDownloading " + date.strftime("%Y-%m-%d") + "...")  
        date = date.strftime("%Y-%m-%d")
        hours = list(group.strftime("%H:%M"))
        
        if not(args.test):
            for data_origin, variable, variables in datas:
                subprocess.run(["mkdir", "-p", os.path.join(folder_path, variable, year, month)])
                
                variables_to_download = {
                    'product_type': 'reanalysis',
                    'format': 'grib',
                    'variable': variables,
                    'year': year,
                    'month': month,
                    'day': day,
                    'time': hours,
                }
                variables_to_download.update(({'pressure_level': ['1000', '925', '850', '700', '600', '500', '400', '300', '250', '200', '150', '100', '50']} if variable == "pressure_variables" else {}))
                
                c.retrieve(
                data_origin,
                variables_to_download,
                target=os.path.join(folder_path, variable, year, month, date + "_ERA5.grib")
                )
            
            when = np.sort(np.unique(np.concatenate([when, group])))
        else:
            print(f"Test: would have downloaded {date}.")
        
    except:
        print("Error downloading " + str(date) + ".")
        with open("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/repos/Scripts/Outputs/failed.txt", 'a') as file:
            file.write(str(date) + "\n")
    

pd.Series(when).to_csv("/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/AI-models-input/when.csv", index = False, header=False)

      