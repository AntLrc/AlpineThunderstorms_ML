# Not tested yet

import xarray as xr
import numpy as np
import pandas as pd
import os
import pickle

import logging

LOG = logging.getLogger(__name__)

def clip_data(ds, latmin, latmax, lonmin, lonmax):
    """
    Clip data to a specific region.
    
    Parameters
    ----------
    ds : xarray.Dataset
        Dataset to clip.
    latmin : float
        Minimum latitude.
    latmax : float
        Maximum latitude.
    lonmin : float
        Minimum longitude.
    lonmax : float
        Maximum longitude.
    
    Returns
    -------
    xarray.Dataset
        Clipped dataset.
    """
    ds = ds.sel(lat=slice(latmin, latmax), lon=slice(lonmin, lonmax))
    return ds

def clip_file(path, latmin, latmax, lonmin, lonmax, output_path=None):
    """
    Clip a file to a specific region.
    
    Parameters
    ----------
    path : str
        Path to the file to clip.
    latmin : float
        Minimum latitude.
    latmax : float
        Maximum latitude.
    lonmin : float
        Minimum longitude.
    lonmax : float
        Maximum longitude.
    output_path : str, optional
        Path to the output file. If None, the input file is overwritten.
    """
    ds_ST = xr.open_dataset(path + "_ST.nc", engine="netcdf4")
    ds_ST_clipped = clip_data(ds_ST, latmin, latmax, lonmin, lonmax)
    del ds_ST
    
    ds_LT = xr.open_dataset(path + "_LT.nc", engine="netcdf4")
    ds_LT_clipped = clip_data(ds_LT, latmin, latmax, lonmin, lonmax)
    del ds_LT
    
    ds_clipped = xr.concat([ds_ST_clipped, ds_LT_clipped], dim="time")
    
    os.remove(path + "_ST.nc")
    os.remove(path + "_LT.nc")
    if output_path is None:
        output_path = path[:-3] + "_clipped.nc"

    LOG.info(f"Saving to {output_path}")
    ds_clipped.to_netcdf(output_path, engine="netcdf4")
    return