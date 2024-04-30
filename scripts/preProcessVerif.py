import sys
import os

import argparse

import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='Preprocess verification data.')

    parser.add_argument("--year", "-y",
                        type=str,
                        required=True,
                        help="Year to verify for files, format YYYY.")

    parser.add_argument("--month", "-m",
                        type=str,
                        required=True,
                        help="Month to verify for files, format mm.")

    parser.add_argument("--step", "-s",
                        type=str,
                        required=True,
                        help="Step to verify for files.")

    parser.add_argument("--dirpath", "-d",
                        type=str,
                        required=True,
                        help="Path to the directory to verify."
                        )

    args = parser.parse_args()

    year = args.year
    month = args.month
    step = args.step
    dirpath = args.dirpath

    if not (step in ["download", "postprocessing", "clipexport"]):
        raise ValueError("Invalid step, must be in 'download', 'postprocessing' or 'clipexport'.")

    if step == "download":
        folderpath = os.path.join(dirpath, year, month)
        if not os.path.exists(os.path.join(folderpath, f"{year}-{month}_ERA5_surface.grib")):
            print(f"Missing ERA5 surface data for {year}-{month}.")
        if not os.path.exists(os.path.join(folderpath, f"{year}-{month}_ERA5_upper.grib")):
            print(f"Missing ERA5 upper data for {year}-{month}.")
        else:
            print(f"ERA5 data for {year}-{month} is complete.")

    if step == "postprocessing":
        finished = True
        folderpath = os.path.join(dirpath, year, month)
        for day in range(1, pd.to_datetime(f"{year}-{month}").days_in_month + 1):
            day = f"{day:02}"
            for hour in range(24):
                hour = f"{hour:02}"
                if not os.path.exists(os.path.join(folderpath, f"pangu_weather_{year}-{month}-{day}T{hour}_LT.nc")):
                    print(f"Missing postprocessed data for {year}-{month}-{day}T{hour}_LT.")
                    finished = False
                else:
                    wholemonth = False
                if not os.path.exists(os.path.join(folderpath, f"pangu_weather_{year}-{month}-{day}T{hour}_ST.nc")):
                    print(f"Missing postprocessed data for {year}-{month}-{day}T{hour}_ST.")
                    finished = False
                else:
                    wholemonth = False
        if finished:
            print(f"Postprocessing for {year}-{month} is complete.")
        if wholemonth:
            print(f"\n\tWhole month of {year}-{month} is missing.")

    if step == "clipexport":
        finished = True
        wholemonth = True
        folderpath = os.path.join(dirpath, year, month)
        for day in range(1, pd.to_datetime(f"{year}-{month}").days_in_month + 1):
            day = f"{day:02}"
            for hour in range(24):
                hour = f"{hour:02}"
                if not os.path.exists(os.path.join(folderpath, f"pangu_weather_{year}-{month}-{day}T{hour}_clipped.nc")):
                    print(f"Missing clipped data for {year}-{month}-{day}T{hour} clipped.")
                    finished = False
                else:
                    print(f"\t Clipped data for {year}-{month}-{day}T{hour}.")
                    wholemonth = False
        if finished:
            print(f"Clipping and exporting for {year}-{month} is complete.")
            
        if wholemonth:
            print(f"\n\tWhole month of {year}-{month} is missing.")

if __name__ == '__main__':
    main()
