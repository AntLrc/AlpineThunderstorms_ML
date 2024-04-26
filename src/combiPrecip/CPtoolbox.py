import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pyproj import Transformer

    

def extract_dates(filename):
    parts = filename.split("_")
    date1 = pd.to_datetime(parts[-2])
    date2 = pd.to_datetime(parts[-1].split(".")[0])
    return date1, date2

def get_precip(date):
    """
    Get precipitation data for a given date.
    
    Parameters
    ----------
    date : str
        Date in the format 'YYYY-MM-DD HH'.
    
    Returns
    -------
    xarray.Dataset
        Dataset containing precipitation data.
    """
    date = pd.to_datetime(date)
    if date < pd.to_datetime('2023-12-18') or date > pd.to_datetime('2024-03-24'):
        raise ValueError('Date must be between 2024-01-01 and 2024-03-24.')
    # Load dataset
    path = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/CombiPrecip/2024"
    
    # CPC_00060_H_20231218000000_20231224230000.nc
    matching_file = None
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(".nc") and filename.startswith("CPC_00060_H_"):
                date1, date2 = extract_dates(filename)
                if date1 <= date <= date2:
                    matching_file = os.path.join(root, filename)
                    break
        if matching_file:
            break
    
    ds = xr.open_dataset(matching_file)
    
    # Select data for the given date
    ds_date = ds.sel(REFERENCE_TS=date, method='nearest')
    
    return to_WGS(ds_date)

def plot_precip_xr(ds, path_to_folder = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/plots/CombiPrecip", **kwargs):
    """
    Plot precipitation data for a given date.
    
    Parameters
    ----------
    ds : xarray.Dataset
        Dataset containing precipitation data.
    """
    
    # Plot data
        
    data_crs = ccrs.PlateCarree()
    ax = plt.subplot(projection = ccrs.Orthographic(8,46.65))
    # Plots the color bar with the same vertical size of the plot
    ds.CPC.plot(transform = data_crs, cmap = 'viridis', cbar_kwargs = {'shrink': 0.6}, ax = ax)
    ax.add_feature(cfeature.BORDERS)
    extent = kwargs.get('extent', [5,11, 45.15, 48.15])
    ax.set_extent(extent)
    plt.show()
    try:
        plt.savefig(os.path.join(path_to_folder, str(ds.time.values[0])[:16] + "_CPC-CombiPrecip.png"))
    except:
        raise ValueError("path_to_folder should be formatted as path/to/folder")
    plt.close()
    return

def plot_precip_str(date, path_to_folder = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/plots/CombiPrecip", **kwargs):
    """
    Plot precipitation data for a given date.
    
    Parameters
    ----------
    date : str
        Date in the format 'YYYY-MM-DD HH'.
    """
    ds = get_precip(date)
    plot_precip_xr(ds, path_to_folder, **kwargs)

def plot_precip(precip, path_to_folder = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/plots/CombiPrecip", **kwargs):
    if type(precip) == str:
        plot_precip_str(precip, path_to_folder, **kwargs)
    elif type(precip) == xr.Dataset:
        plot_precip_xr(precip, path_to_folder, **kwargs)
    else:
        raise ValueError("precip must be a string or xarray.Dataset")
    
    
def to_WGS(ds):
    """Convert the coordinates of xarray.Dataset ds from LV95 to WGS84

    Parameters
    ----------
    ds : xarray.Dataset
        Dataset containing the data to convert, with in its coordinates the variables 'x' and 'y' in LV95 coordinates.
    """
    transformer = Transformer.from_proj(2056, 4326, always_xy=True)
    xx, yy = np.meshgrid(ds.x.values, ds.y.values)
    lon, lat = transformer.transform(xx, yy)
    if ds.REFERENCE_TS.size > 1:
        res = xr.Dataset(
            {
                "CPC": (["time", "latitude", "longitude"], ds.CPC.values),
            },
            coords={
                "latitude": (["latitude", "longitude"], lat),
                "longitude": (["latitude", "longitude"], lon),
                "time": (["time"], ds.REFERENCE_TS.values),
            },
            attrs={
                
            }
        )
    else:
        res = xr.Dataset(
            {
                "CPC": (["time", "latitude", "longitude"], np.array([ds.CPC.values])),
            },
            coords={
                "latitude": (["latitude", "longitude"], lat),
                "longitude": (["latitude", "longitude"], lon),
                "time": (["time"], np.array([ds.REFERENCE_TS.values])),
            },
        )
    
    res["longitude"].attrs = {
        "units": "degrees_east",
        "long_name": "longitude values",
        "axis": "X",
        "standard_name": "longitude"
    }
    
    res["latitude"].attrs = {
        "units": "degrees_north",
        "long_name": "latitude values",
        "axis": "Y",
        "standard_name": "latitude"
    }
    
    res["CPC"].attrs = {
        "units": "mm/h",
        "long_name": "Precipitation rate",
        "standard_name": "CPC"
    }    
    
    res["time"].attrs = {
        "long_name": "time in hours UTC",
        "standard_name": "time",
        "calendar": "gregorian"
    }
    
    return res


