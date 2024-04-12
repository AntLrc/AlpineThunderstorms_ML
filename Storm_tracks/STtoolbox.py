#%%

import pandas as pd
import numpy as np
import geopandas as gpd
import xarray as xr
import pickle
from shapely.geometry import Point, LineString


def to_WGS():
    """
    Convert the coordinates of severe storms from Swiss coordinates (EPSG:2056) to WGS84 coordinates (EPSG:4326).
    
    This function reads a CSV file containing severe storm data with Swiss coordinates, converts the coordinates to WGS84,
    and saves the updated data to a new CSV file.
    """
    path = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/severe_storms_2016-2021/CH_severe_storms_2016_2021.csv"

    df = pd.read_csv(path, sep=';', dtype=str, index_col=False)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.chx, df.chy), crs="EPSG:21781")
    gdf_wgs = gdf.to_crs("EPSG:4326")
    wgsx = []
    wgsy = []

    for p in gdf_wgs.geometry:
        x, y = p.coords[0]
        wgsx.append(x)
        wgsy.append(y)

    res = df.drop(["chx", "chy", "Unnamed: 0"], axis=1)
    res["longitude"] = wgsx
    res["latitude"] = wgsy
    res["time"] = df["time"].apply(lambda x : x[0:4] + '-' + x[4:6] + '-' + x[6:8] + 'T' + x[8:10] + ':' + x[10:12]+":00+00:00")

    res.to_csv("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/Storm_tracks/CH_severe_storms_2016_2021_WGS84.csv", index = False)

def to_datetime():
    """
    Convert the date and time of severe storms to a datetime object.
    
    This function reads a CSV file containing severe storm data with a date and time column, and converts the date and time to a datetime object.
    """
    path = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/severe_storms_2016-2021/CH_severe_storms_2016_2021.csv"
    df = pd.read_csv(path, sep = ";", dtype=str, index_col=False)
    df["time"] = df["time"].apply(lambda x : x[0:4] + '-' + x[4:6] + '-' + x[6:8] + 'T' + x[8:10] + ':' + x[10:12]+":00+00:00")
    df.to_csv("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/Storm_tracks/CH_severe_storms_2016_2021.csv", index = False)

def extract_date(date):
    """
    Extract the storms that occurred on a specific date, and return them as a 
    pandas DataFrameGroupBy object.

    Parameters
    ----------
    date : str
        The date to extract, formatted as "yyyy-mm-dd".

    Returns
    -------
    pandas.core.groupby.DataFrameGroupBy
        The storms that occurred on the specified date.
    """
    path = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/Storm_tracks/CH_severe_storms_2016_2021_WGS84.csv"
    try:
        df = pd.read_csv(path, dtype = {"ID" : str}, parse_dates=["time"])
    except FileNotFoundError:
        raise FileNotFoundError("CSV file not found.")  
    
    storms1 = df.loc[(df["time"].dt.date >= pd.to_datetime(date).date()) & (df["time"].dt.date < pd.to_datetime(date).date() + pd.Timedelta(days=1))].groupby("ID")
    
    return storms1

def to_pickle(frompath = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/Storm_tracks/CH_severe_storms_2016_2021_WGS84.csv", topath = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/Storm_tracks/CH_severe_storms_2016_2021_WGS84.pkl"):
    """
    Convert a CSV file containing severe storm data to a pickle file of a DataFrameGroupBy object, grouped by storm ID.
    
    Parameters
    ----------
    frompath : str
        The path to the CSV file.
    topath : str
        The path to save the pickle file.
    """
    df = pd.read_csv(frompath, dtype = {"ID" : str}, parse_dates=["time"])
    res = df.groupby("ID")
    with open(topath, 'wb') as f:
        pickle.dump(res, f)
    return

def get_storms(path = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/Storm_tracks/CH_severe_storms_2016_2021_WGS84.pkl"):
    """
    Load the severe storm data from a pickle file and return it as a DataFrameGroupBy object.
    
    Returns
    -------
    pandas.core.groupby.DataFrameGroupBy
        The severe storm data, grouped by storm ID.
    """
    try:
        with open(path, 'rb') as f:
            res = pickle.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("Pickle file not found.")
    return res

def tracks_df(storms = get_storms()):
    """
    Create a DataFrame containing the tracks of severe storms. Ignores single-point storms.
    
    Parameters
    ----------
    storms : pandas.core.groupby.DataFrameGroupBy
        DataFrameGroupBy object containing storm data.
    
    Returns
    -------
    geopandas.geodataframe.GeoDataFrame
        GeoDataFrame containing the storm tracks.
    """
    
    track_geoms = []
    
    for storm_ID, group in storms:
        track_geom = track(group)
        track_geoms.append({'ID': storm_ID, 'geometry': track_geom})
    gdf = gpd.GeoDataFrame(track_geoms, crs="EPSG:4326")
    
    return gdf

def track(storm):
    """
    Create a LineString object representing the track of a severe storm.
    
    Parameters
    ----------
    storm : pandas.core.frame.DataFrame
        DataFrame containing the storm data.
    
    Returns
    -------
    shapely.geometry.linestring.LineString
        LineString object representing the storm track.
    """
    points = [Point(x, y) for x, y in zip(storm["longitude"], storm["latitude"])]
    if len(points) == 1:
        track = points[0]
    else:
        track = LineString(points)
    return track

def save_tracks(gdf = tracks_df(), path = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/Storm_tracks/CH_severe_storm_tracks_2016_2021.pkl"):
    """
    Save the storm tracks to a pickle file.
    
    Parameters
    ----------
    gdf : geopandas.geodataframe.GeoDataFrame
        GeoDataFrame containing the storm tracks.
    path : str
        Path to save the pickle file.
    """
    with open(path, 'wb') as f:
        pickle.dump(gdf, f)
    return

def get_storms_tracks(path = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/Storm_tracks/CH_severe_storm_tracks_2016_2021.pkl"):
    """
    Load the storm tracks from a pickle file.
    
    Parameters
    ----------
    path : str
        Path to the pickle file.
    
    Returns
    -------
    geopandas.geodataframe.GeoDataFrame
        GeoDataFrame containing the storm tracks.
    """
    with open(path, 'rb') as f:
        gdf = pickle.load(f)
    return gdf

def needed_times(dated_storms = pd.read_csv("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/Storm_tracks/CH_severe_storms_2016_2021.csv", parse_dates=["time"]),
                 lead_times = [pd.Timedelta(hours = i) for i in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,27,30,33,36,42,48,60,72]],
                 ):
    res1 = dated_storms["time"][dated_storms["time"].dt.minute == 0].unique()
    for dtimes in lead_times:
        res1 = np.concatenate((res1, res1 - dtimes))
    res1 = np.unique(res1).sort()
    
    with open("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/ERA5/needed_times.pkl", 'wb') as f:
        pickle.dump(res1, f)
    return res1
    
    

    

# %%
