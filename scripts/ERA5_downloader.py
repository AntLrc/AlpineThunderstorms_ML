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

parser.add_argument("--surface","-s",
                    action="store_true",
                    help="Downloading only surface field if present.")

parser.add_argument("--pressure","-p",
                    action="store_true",
                    help="Downloading only pressure-dependant field if present.")

parser.add_argument("--year",
                    type=str,
                    help = "Year to download, format YYYY")

parser.add_argument("--month",
                    type=str,
                    help = "Month to download, format MM")

parser.add_argument("--test",
                    action="store_true",
                    help="Test the downloader.")

args = parser.parse_args()

folder_path =  args.output


datas = [('reanalysis-era5-single-levels',
          "surface",
          ['mean_sea_level_pressure', '10m_u_component_of_wind', '10m_v_component_of_wind', '2m_temperature'])]*(args.surface or not(args.surface or args.pressure)) +\
    [('reanalysis-era5-pressure-levels',
      "upper",
      ['geopotential', 'specific_humidity', 'temperature', 'u_component_of_wind', 'v_component_of_wind'])]*(args.pressure or not(args.surface or args.pressure))



c = cdsapi.Client()



year, month = args.year, args.month
print(f"Downloading {year}-{month}...")

# Get the days of the month as two-digit int
days = [f"{num:02}" for num in range(1, pd.to_datetime(f"{year}-{month}").days_in_month + 1)]
hours = [f"{i:02}" for i in range(24)]


for data_origin, variable, variables in datas:
    if not(args.test):
        try:
            os.makedirs(os.path.join(folder_path, year, month), exist_ok=True)
            
            variables_to_download = {
                'product_type': 'reanalysis',
                'format': 'grib',
                'variable': variables,
                'year': year,
                'month': month,
                'day': days,
                'time': hours,
            }
            variables_to_download.update(({'pressure_level': ['1000', '925', '850', '700', '600', '500', '400', '300', '250', '200', '150', '100', '50']} if variable == "upper" else {}))
            
            c.retrieve(
            data_origin,
            variables_to_download,
            target=os.path.join(folder_path, year, month, f"{year}-{month}_ERA5_{variable}.grib")
            )
        except:
            print(f"Error downloading {year}-{month} for {variable} variables.")
            with open("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/repos/Scripts/Outputs/failed.txt", 'a') as file:
                file.write(f"{year}-{month}_{variable}\n")
    else:
        print(f"Test: would have downloaded {year}-{month} for {variable} variables.")
        print(os.path.join(folder_path, year, month, f"{year}-{month}_ERA5_{variable}_ERA5.grib"))

      