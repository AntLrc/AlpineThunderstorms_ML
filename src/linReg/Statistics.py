import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.interpolate import RegularGridInterpolator
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pwOutputs.PWtoolbox as pwtb
import swissMetNet.SMNtoolbox as smntb
import stormTracks.STtoolbox as sttb


def loadData(**kwargs):
    """
    Returns interpolated data of PW outputs over stations from SwissMetNet, 
    either by intersecting dataVars from dirnameStations and dirnamePX,
    or by opening fromFile.
    
    Parameters
    ----------
    **kwargs : dict
        Keyword arguments.
        These can include:
            fromFile: str
                The file to load data from.
            dataVars : list
                List of data variables to load.
            dirnameStations : str
                The directory to load station data from.
            dirnamePW : str
                The directory to load PW output data from.
            minyear : int
                The minimum year to load data from.
            maxyear : int
                The maximum year to load data from.
            minmonth : int
                The minimum month to load data from.
            maxmonth : int
                The maximum month to load data from.
            stormFile : str
                The file to load storm data from.
            stormDateIDFile : str
                The file to load storm date IDs from.
        - coord : str
            The CRS of the storm data coordinates.
        - coords : tuple
            The names of the columns containing the storm data coordinates.
    
    Returns
    -------
    result : xarray.Dataset
        The interpolated data.
    """
    fromFile = kwargs.get("fromFile", None)
    if fromFile:
        print(f"Loading data from {fromFile}", flush = True)
        result = xr.open_dataset(fromFile)
    else:
        dataVars = kwargs.get("dataVars", "all")
        dirnameStations = kwargs.get("dirnameStations")
        dirnamePW = kwargs.get("dirnamePW")
        if dataVars != "all" and dataVars != ["all"]:
            dataVarsStations = list(set(dataVars) & set(["all", "precip", "wind gust"]))
            dataVarsPW = list(set(dataVars) & set(["all", "t2m", "msl", "u10", "v10"]))
        else:
            dataVarsStations = "all"
            dataVarsPW = "all"
        print(f"Loading data from {dirnameStations} and {dirnamePW}", flush=True)
        dsPW = pwtb.loadData(dataVarsPW, dirnamePW, **kwargs)
        dsSMN = smntb.loadData(dataVarsStations, dirnameStations, **kwargs)
        
        print("Interpolating data", flush=True)
        interpolation = [None]*len(dsPW.lead_time.values)
        for i in range(len(dsPW.lead_time.values)):
            interpolation[i] = dsPW.sel(time = dsSMN.time, lead_time = dsPW.lead_time.values[i]).interp(lon = dsSMN.longitude.where(dsSMN.station == dsSMN.station), lat = dsSMN.latitude.where(dsSMN.station == dsSMN.station))

        print("Concatenating data")
        interpolation = xr.concat(interpolation, dim = "lead_time")
        interpolation = xr.merge((interpolation, dsSMN))
        
        result = interpolation
    
    if kwargs.get("stormFile", None):
        minyear, maxyear = kwargs.get("minyear", 2016), kwargs.get("maxyear", 2021)
        minmonth, maxmonth = kwargs.get("minmonth", 1), kwargs.get("maxmonth", 12)
        mindate = pd.Timestamp(f"{minyear}-{minmonth}-01 00:00:00")
        maxdate = pd.Timestamp(f"{maxyear}-{maxmonth}-01 00:00:00") + pd.DateOffset(months=1) - pd.DateOffset(hours=1)
        
        print("Loading storm data", flush = True)
        storms = sttb.loadStorms(kwargs.get("stormFile"))
        storms["time"] = storms["time"].dt.tz_localize(None)
        
        storms = sttb.filter(storms, maxdate = maxdate, mindate = mindate)

        stormsDateID = sttb.loadStorms(kwargs.get("stormDateIDFile"))
        stormsDateID.index = stormsDateID.index.tz_localize(None)
        stormsDateID.sort_index(inplace=True)
        stormsDateID = stormsDateID.loc[mindate:maxdate]

        times = result.time.values
        stations = result.station.values

        nearest_storm = np.array([[""]*len(stations)]*len(times), dtype=object)
        distance = np.array([[np.inf]*len(stations)]*len(times))

        print("Finding nearest storms", flush = True)
        for i in range(len(times)):
            print(f"{i/len(times)*100:.2f} %", end='\r', flush = True)
            lon,lat = result.sel(time=times[i]).longitude.values, result.sel(time=times[i]).latitude.values
            ids, dist = sttb.nearestStorm(storms, stormsDateID, lon,lat,times[i], **kwargs)
            nearest_storm[i] = ids
            distance[i] = dist
        
        result["nearest_storm"] = xr.DataArray(nearest_storm, coords=[result.time, result.station], dims=["time", "station"])
        result["distance"] = xr.DataArray(distance, coords=[result.time, result.station], dims=["time", "station"])
        
    
    if "latitude" in result.coords and "lat" in result.coords:
        result = result.drop_vars("lat")
    if "longitude" in result.coords and "lon" in result.coords:
        result = result.drop_vars("lon")
    
    if "time" in result.coords["latitude"].dims:
        result["latitude"] = result["latitude"].mean(dim = "time")
    if "time" in result.coords["longitude"].dims:
        result["longitude"] = result["longitude"].mean(dim = "time")
    
    return result

def saveData(data, toFile, **kwargs):
    """
    Save data to a file.
    
    Parameters
    ----------
    data : xarray.Dataset
        The data to save.
    **kwargs : dict
        Additional keyword arguments to be passed to the to_netcdf method.
        dirpath : str
            The directory to save the file to.
    """
    dirpath = kwargs.pop("dirpath", None)
    if dirpath is not None:
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        toFile = os.path.join(dirpath, toFile.split("/")[-1])
    data.to_netcdf(toFile, **kwargs)
    return

def plotData(data, **kwargs):
    
    storms_only = kwargs.get("storms_only", False)
    
    
    return

def InverseDistanceWeightedGust(distance, wind_gust, alpha, **kwargs):
    """
    Calculate the inverse distance weighted gust.
    
    Parameters
    ----------
    distance : xarray.DataArray
        The distance to the nearest storm.
    wind_gust : xarray.DataArray
        The wind gust data.
    alpha : float
        The alpha parameter of weight.
    **kwargs : dict
        Additional keyword arguments.
        These can include:
            dim : str
                The dimension to sum over.
    
    Returns
    -------
    result : xarray.DataArray
        The inverse distance weighted gust.
    """
    dim = kwargs.get("dim", "station")
    result = (wind_gust/(distance**alpha)).sum(dim=dim)/(1/(distance**alpha)).sum(dim=dim)
    return result