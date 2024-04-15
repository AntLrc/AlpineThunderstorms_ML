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

class CustomAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values.lower() == 'surface':
            setattr(namespace,
                    self.dest,
                    ('reanalysis-era5-single-levels',
                     'surface_variables',
                     )
                    )
        elif values.lower() == 'pressure':
            setattr(namespace,
                    self.dest,
                    ('reanalysis-era5-pressure-levels',
                     'pressure_variables'
                     )
                    )
        else:
            parser.error("Invalid value for --var-type argument. Use 'surface' or 'pressure'.")

folder_path = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/AI-models-input"
    
parser = argparse.ArgumentParser(description="Download ERA5 data")

parser.add_argument("--dates", type=str,
                    help="Dates to download, stored in a pkl file containing a DataFrame indexed by timestamp.")
parser.add_argument("--var_type", action=CustomAction, type=str,
                    help="Type of variable to download. Use 'surface' or 'pressure'.")
parser.add_argument("--year", type=str, default=False,
                    help = "Year to download.")
parser.add_argument("--month", type=str, default=False,
                    help = "Month to download.")
parser.add_argument("--min_day", type=str, default=False,
                    help = "Minimum day to download.")
parser.add_argument("--max_day", type=str, default=False,
                    help = "Maximum day to download.")

args = parser.parse_args()

dates_file = args.dates
with open(dates_file, 'rb') as f:
    dates = pickle.load(f)
    
with open("/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/AI-models-input/whatwhen.pkl", 'rb') as f:
    whenwhat = pickle.load(f)
    
data_origin, folder = args.var_type
year_pars = args.year
month_pars = args.month

target_folder = folder_path + "/" + folder + "/"

print("Downloading " + folder + "...")

c = cdsapi.Client()

dates_gr = dates.groupby(dates.index.date)

for date, group in dates_gr:
    try:
        print("Downloading " + date.strftime("%Y-%m-%d") + "...")    
        year, month, day = date.strftime("%Y"), date.strftime("%m"), date.strftime("%d")
        if year_pars:
            if year != year_pars:
                continue
        if month_pars:
            if month != month_pars:
                continue
        if args.min_day and day < args.min_day:
            continue
        if args.max_day and day > args.max_day:
            continue
        
        date = date.strftime("%Y-%m-%d")
        hours = list(group.index.strftime("%H:%M"))
        variables = group[folder].iloc[0]
        subprocess.run(["mkdir", "-p", target_folder + year + "/" + month])
        
        
        
        
        c.retrieve(
        data_origin,
        {
            'product_type': 'reanalysis',
            'format': 'grib',
            'variable': variables,
            'year': year,
            'month': month,
            'day': day,
            'time': hours,
        },
        target=target_folder + year + "/" + month + "/" + date + "_ERA5.grib"
        )
        
        whenwhat = pd.concat([whenwhat, group])
    
    except:
        print("Error downloading " + str(date) + ".")
        with open("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/repos/Scripts/Outputs/failed.txt", 'a') as file:
            file.write(str(date) + "\n")

with open("/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/AI-models-input/whatwhen.pkl", 'wb') as f:
    pickle.dump(whenwhat, f)

      