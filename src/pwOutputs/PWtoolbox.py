import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
import os
from collections import defaultdict


# I need to think more about how to qualify the date : is it the date at which the forecast is made, or the forecasted date? What about the boundaries then?

def loadData(data_vars, dirname, **kwargs):
    """
    Load data from a directory.
    
    Parameters
    ----------
    data : str or list
        The type of data to load, as output of PanguWeather / ERA5.
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
            lead_times : list
                The lead times to load data for.
    
    Returns
    -------
    res : xarray.Dataset
        The loaded data.
    """
    lead_times = kwargs.get('lead_times', [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24, 27, 30, 33, 36, 42, 48, 60, 72])
    minyear = kwargs.get('minyear', 2016)
    maxyear = kwargs.get('maxyear', 2024)
    minmonth = kwargs.get('minmonth', 1)
    maxmonth = kwargs.get('maxmonth', 12 if maxyear != 2024 else 3)
    
    mindate = pd.to_datetime(f"{minyear}-{minmonth}-01T00:00:00")
    maxdate = pd.to_datetime(f"{maxyear}-{maxmonth}-01T00:00:00") + pd.DateOffset(months = 1) - pd.DateOffset(hours = 1)
    
    files = filesForDates(dirname,
                          mindate - pd.DateOffset(hours = max(lead_times)),
                          maxdate - pd.DateOffset(hours = min(lead_times)))
    # We load the files which contain a prediction in the expected range of dates
    
    res = defaultdict(list)
    for file, date in files:
        data = xr.open_dataset(file, engine = "netcdf4")
        
        if data_vars != "all":
            data = data[data_vars]
        
        for j in range(len(lead_times)):
            cdate = (date + pd.DateOffset(hours = lead_times[j])).to_datetime64() #The date of the forecast
            # Some nan values are to be expected on the time borders
            if cdate >= mindate and cdate <= maxdate:
                tmp = data.where(data.time == cdate, drop = True)
                tmp = tmp.expand_dims(dim = "lead_time", axis = 0)
                tmp = tmp.assign_coords({"lead_time":("lead_time", [lead_times[j]])})
                res[cdate].append(tmp)
            
    resf = []
    datesf = np.sort(np.array(list(res.keys())))

    for date in datesf:
        resf.append(xr.concat(reversed(res[date]), dim = "lead_time"))

    result = xr.concat(resf, dim = "time")
    
    return result

def filesForDates(dirname, mindate, maxdate):
    """
    Get all files in a directory that are in a given date range.
    
    Parameters
    ----------
    dirname : str
        The directory to get files from.
    mindate : pd.Timestamp
        The minimum date to get files from.
    maxdate : pd.Timestamp
        The maximum date to get files from.
    
    Returns
    -------
    files : list
        List of files with corresponding prediction date.
    """
    res = []
    for root, dirs, files in os.walk(dirname):
        for file in files:
            date = fileDate(file)
            if fileDate(file) >= mindate and fileDate(file) <= maxdate:
                res.append((os.path.join(root,file), date))
    res.sort()
    return res

def fileDate(file):
    """
    Get the date of a file formatted as a PanguWeather clipped output.
    
    Parameters
    ----------
    file : str
        The file name.
    
    Returns
    -------
    date : pd.Timestamp
        The date of the file.
    """
    return pd.to_datetime(file.split("_")[-2])
    
def saveData(data, toFile, **kwargs):
    """
    Save data to a file.
    
    Parameters
    ----------
    data : xarray.Dataset
        The data to save.
    toFile : str
        The file to save the data to.
    **kwargs : dict
        Additional keyword arguments to be passed to the to_netcdf method.
    
    Returns
    -------
    None
    """
    data.to_netcdf(toFile, **kwargs)
    return