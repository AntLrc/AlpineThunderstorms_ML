import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
import matplotlib.pyplot as plt
import os
import sys

def loadData(data_vars, dirname, **kwargs):
    """
    Load data from a directory.
    
    Parameters
    ----------
    data_vars : str
        The type of data to load, either 'precip', 'wind gust' or 'all'.
    dirname : str
        The directory to load data from.
    **kwargs : dict
        Additional keyword arguments.
        These can include:
            minyear : int
                The minimum year to load data from.
            maxyear : int
                The maximum year to load data from.
            minmonth : int
                The minimum month to load data from.
            maxmonth : int
                The maximum month to load data from.
            stations : list
                A list of stations to load data from.
    """
    data_vars = ["precipitation_amount"]*(data_vars == "precip" or data_vars == "all") + ["wind_speed_of_gust"]*(data_vars == "wind gust" or data_vars == "all")
    if len(data_vars) == 0:
        raise ValueError("Invalid data type, data must be in 'precip', 'wind gust' or 'all'.")
    
    minyear = kwargs.get('minyear', 2016)
    maxyear = kwargs.get('maxyear', 2024)
    minmonth = kwargs.get('minmonth', 1)
    maxmonth = kwargs.get('maxmonth', 12 if maxyear != 2024 else 3)
    stations = kwargs.get('stations', "all")
    if not(isinstance(stations, list)) and stations != "all":
        raise ValueError("Invalid stations type, stations must be a list of stations or 'all'.")
    files = filesForDates(dirname, pd.to_datetime(f"{minyear}-{minmonth}"), pd.to_datetime(f"{maxyear}-{maxmonth}"))
    res = None
    for file in files:
        print(file)
        data = xr.open_dataset(os.path.join(dirname,file), engine = "netcdf4")
        data = data[data_vars]
        if stations != "all":
            data = data.where(data["station"].isin(stations), drop = True)
        if res is None:
            res = data
        else:
            res = xr.concat([res, data], dim = "time")
    
    return res
        
def filesForDates(dirname, mindate, maxdate):
    """
    Get all files in a directory that are in a given date range.
    
    Parameters
    ----------
    dirname : str
        The directory to search.
    mindate : datetime
        The minimum date.
    maxdate : datetime
        The maximum date.
    
    Returns
    -------
    list
        A list of files in the directory that are in the given date range.
    """
    files = os.listdir(dirname)
    files = [f for f in files if f.endswith(".nc")]
    files = [f for f in files if pd.to_datetime(f"{f[-9:-5]}-{f[-5:-3]}") >= mindate and pd.to_datetime(f"{f[-9:-5]}-{f[-5:-3]}") <= maxdate]
    files.sort()
    return files

