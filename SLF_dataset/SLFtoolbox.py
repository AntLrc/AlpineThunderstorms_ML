#%%

import pandas as pd
import pickle
import numpy as np
import geopandas as gpd
import xarray as xr
from shapely.geometry import LineString, Point




def extract_station(filename = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/SLF_dataset/measurement-data.slf.ch/imis/stations.csv"):
    """
    Extract the station data from the CSV file and return it as a GeoDataFrame object.
    
    Parameters
    ----------
    filename : str
        The path to the CSV file.
    
    Returns
    -------
    geopandas.geodataframe.GeoDataFrame
        The station data.
    """
    
    df = pd.read_csv(filename)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["lon"], df["lat"]), crs="EPSG:4326")
    gdf.drop(columns=["lon", "lat"], inplace=True)
    
    return gdf

def stations_to_pickle(gdf = extract_station(), path = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/SLF_dataset/stations.pkl"):
    """
    Save an object to a pickle file.
    
    Parameters
    ----------
    obj : object
        The object to save.
    path : str
        The path to the pickle file.
    """
    
    with open(path, 'wb') as f:
        pickle.dump(gdf, f)
    
    return

def get_stations(path = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/SLF_dataset/stations.pkl"):
    """
    Load the station data from a pickle file.
    
    Parameters
    ----------
    path : str
        The path to the pickle file.
    
    Returns
    -------
    object
        The object saved in the pickle file.
    """
    
    with open(path, 'rb') as f:
        gdf = pickle.load(f)
    
    return gdf

def station_nearby(pos, dist, stations = get_stations(), pos_coord = "EPSG:4326"):
    """
    Find the stations within a certain radius of a pos (Point). The Earth is assumed to be a sphere, which results in a slight overestimation of the distance.
    
    Parameters
    ----------
    pos : shapely.geometry.point.Point
        The position around which to search for stations.
    dist : float
        The maximum distance to pos, in km.
    stations : geopandas.geodataframe.GeoDataFrame
        The station data, in WGS84 or LV95.
        
    Returns
    --------
    list
        The station_code of stations within the radius.
    """
    if stations.crs == "EPSG:4326": #Projecting on LV95 to get accurate distances.
        stations = stations.to_crs("EPSG:2056")
    elif stations.crs != "EPSG:2056":
        raise ValueError("The crs of the stations is not recognized.")
    
    if pos_coord == "EPSG:4326" or pos_coord == "EPSG:21781":
        gdf = gpd.GeoDataFrame({"geometry": [pos]}, crs=pos_coord)
        gdf = gdf.to_crs("EPSG:2056")
        pos = gdf["geometry"].values[0]
    else:
        raise ValueError("The crs of the position is not recognized.")
    res = stations[stations.distance(Point(pos)) < dist*1000]["station_code"].values
    return res


# %%
