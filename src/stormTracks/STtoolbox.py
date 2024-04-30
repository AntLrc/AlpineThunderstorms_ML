import pandas as pd
import numpy as np
import geopandas as gpd
import xarray as xr
import pickle
import pyproj
from shapely.geometry import Point, LineString
from collections import defaultdict

def changeCoord(df, from_crs = "EPSG:21781", to_crs = "EPSG:4326", **kwargs):
    """
    Change the coordinates of a DataFrame from one CRS to another via a GeoDataFrame.
    
    Parameters
    ----------
    df : pandas.core.frame.DataFrame.
        DataFrameobject containing the data.
    from_crs : str
        The CRS of the input coordinates, by default LV03 (EPSG:21781).
    to_crs : str
        The CRS to convert the coordinates to, by default WGS84 (EPSG:4326).
    **kwargs : dict
        Keyword arguments specifying the columns containing the x and y coordinates.
        The valid keyword arguments are:
    """    
    # Getting projections information
    from_crs = pyproj.CRS(from_crs)
    from_x, from_y = kwargs.get("from_coords", (dim.abbrev for dim in from_crs.axis_info))
    
    to_crs = pyproj.CRS(to_crs)
    to_x, to_y = kwargs.get("to_coords", (dim.abbrev for dim in to_crs.axis_info))
    
    # Projecting the coordinates
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[from_x], df[from_y]), crs=from_crs)
    gdf = gdf.to_crs(to_crs)
    
    # Converting back to DataFrame
    x_res = gdf.geometry.x
    y_res = gdf.geometry.y
    
    res = df.drop([from_x, from_y], axis=1)
    res[to_x] = x_res
    res[to_y] = y_res
    
    return res

def loadStorms(fromFile, **kwargs):
    """
    Load severe storm data from a CSV or pickle file.
    
    Parameters
    ----------
    fromFile : str
        The path to the file containing the severe storm data.
    **kwargs : dict
        Keyword arguments specifying the format of the file.
        The valid keyword arguments are:
        - format : str
            The format of the file, either "pkl" or "csv".
        - sep : str
            The separator used in the CSV file.
        - index_col : bool
            Whether to use the first column as the index.
        - parse_dates : str
            The column containing the dates to parse.
        - dtype : dict
            The data types of the columns.
        - time_col : str
            The column containing the time data.
    
    Returns
    -------
    pandas.core.groupby.DataFrame
        DataFrame containing the severe storm data.
    """
    if fromFile.endswith(".pkl") or kwargs.get("format") == "pkl":
        with open(fromFile, 'rb') as f:
            storms = pickle.load(f)
            
    elif fromFile.endswith(".csv") or kwargs.get("format") == "csv":
        if not (kwargs.get("time_col") is None):
            dtype = kwargs.get("dtype", None)
            time_col = kwargs.get("time_col")
            dtype[time_col] = "str"
            storms = pd.read_csv(fromFile,
                            sep = kwargs.get("sep", ","),
                            index_col = kwargs.get("index_col", False),
                            dtype = dtype
                            )
            storms[time_col] = pd.to_datetime(storms[time_col].apply(lambda x : (x[0:4] + '-' + x[4:6] + '-' + x[6:8] + 'T' + x[8:10] + ':' + x[10:12]+":00+00:00")))
            
        else:
            storms = pd.read_csv(fromFile,
                            sep = kwargs.get("sep", ","),
                            index_col = kwargs.get("index_col", False),
                            parse_dates = kwargs.get("parse_dates", None),
                            dtype = kwargs.get("dtype", None)
                            )
    else:
        raise ValueError("Invalid file format.")
    
    return storms
             
def saveStorms(storms, toFile, **kwargs):
    """
    Save severe storm data to a CSV or pickle file. If a GroupBy object, storms will be aggregated to be save as CSV - but not necessarily for pickle.
    
    Parameters
    ----------
    storms : pandas.core.frame.DataFrame or pandas.core.groupby.DataFrameGroupBy
        DataFrame or DataFrameGroupBy containing the severe storm data.
    toFile : str
        The path to save the severe storm data.
    **kwargs : dict
        Keyword arguments specifying the format of the file.
        The valid keyword arguments are:
        - format : str
            The format of the file, either "pkl" or "csv".
        - sep : str
            The separator to use in the CSV file.
        - index : bool
            Whether to include the index in the CSV file.
        - agg : bool
            Whether to aggregate the storms before saving as a pickle file.
    
    Returns
    -------
    None
    """
    if toFile.endswith(".pkl") or kwargs.get("format") == "pkl":
        if kwargs.get("agg", False) and isinstance(storms, pd.core.groupby.DataFrameGroupBy):
            storms = storms.filter(lambda x:True)
        with open(toFile, 'wb') as f:
            pickle.dump(storms, f)
    elif toFile.endswith(".csv") or kwargs.get("format") == "csv":
        if isinstance(storms, pd.core.groupby.DataFrameGroupBy):
            storms = storms.filter(lambda x: True)
        storms.to_csv(toFile, sep = kwargs.get("sep", ","), index = kwargs.get("index", True))
    else:
        raise ValueError("Invalid file format.")
    return
    
def filter(storms, **kwargs):
    """
    Filter severe storms based on the specified criteria.
    
    Parameters
    ----------
    storms : pandas.core.groupby.DataFrameGroupBy or pandas.core.frame.DataFrame or str
        DataFrameGroupBy object containing storm data, or a DataFrame or a path to a CSV or pickle file.
    **kwargs : dict
        Keyword arguments specifying the criteria to filter the storms.
        The valid keyword arguments are:
        - mindate : str
            The minimum date of the storms to keep.
        - maxdate : str
            The maximum date of the storms to keep.
        - minlon : float
            The minimum longitude of the storms to keep.
        - maxlon : float
            The maximum longitude of the storms to keep.
        - minlat : float
            The minimum latitude of the storms to keep.
        - maxlat : float
            The maximum latitude of the storms to keep.
        - agg : bool
            Whether to aggregate the storms before returning.
    
    Returns
    -------
    pandas.core.groupby.DataFrameGroupBy or pandas.core.frame.DataFrame
        DataFrameGroupBy or DataFrame object containing the filtered storms (type depending on kwargs).
    """
    if isinstance(storms, str):
        storms = loadStorms(storms, **kwargs)
        
    if isinstance(storms, pd.DataFrame):
        # if storms is a DataFrame, convert it to a DataFrameGroupBy object
        storms = storms.groupby("ID")
    
    # Filter storms based on the specified criteria
    for key, value in kwargs.items():
        if key == "mindate":
            storms = storms.filter(lambda x: x["time"].dt.date.min() >= pd.to_datetime(value).date()).groupby("ID")
        elif key == "maxdate":
            storms = storms.filter(lambda x: x["time"].dt.date.max() < pd.to_datetime(value).date()).groupby("ID")
        elif key == "minlon":
            storms = storms.filter(lambda x: x["longitude"].min() >= value).groupby("ID")
        elif key == "maxlon":
            storms = storms.filter(lambda x: x["longitude"].max() < value).groupby("ID")
        elif key == "minlat":
            storms = storms.filter(lambda x: x["latitude"].min() >= value).groupby("ID")
        elif key == "maxlat":
            storms = storms.filter(lambda x: x["latitude"].max() < value).groupby("ID")
        elif key == "storm_type":
            if value == "RS":
                storms = storms.filter( lambda x:(x["w_rainstorm"] == 1).all() ).groupby("ID")
            elif value == "SRS":
                storms = storms.filter( lambda x:(x["s_rainstorm"] == 1).all() ).groupby("ID")
            elif value == "HS":
                storms = storms.filter( lambda x:(x["w_hailstorm"] == 1).all() ).groupby("ID")
            elif value == "SHS":
                storms = storms.filter( lambda x:(x["s_hailstorm"] == 1).all() ).groupby("ID")
            elif value == "SC":
                storms = storms.filter( lambda x:(x["supercell"] == 1).all() ).groupby("ID")
            elif value == "OR": 
                storms = storms.filter( lambda x:(x[["w_rainstorm", "s_rainstorm", "w_hailstorm", "s_hailstorm", "supercell"]] == 0).all(axis = 1).all() ).groupby("ID")
            else:
                raise ValueError("Invalid storm type.")
        else:
            if key != "agg":
                raise ValueError("Invalid keyword argument.")
    if kwargs.get("agg", False):
        storms = storms.filter(lambda x: True)
    return storms

def tracks(storms, **kwargs):
    """
    Create a DataFrame containing the tracks of severe storms.
    
    Parameters
    ----------
    storms : pandas.core.groupby.DataFrameGroupBy or pandas.core.frame.DataFrame or str
        DataFrameGroupBy object containing storm data, or a DataFrame or a path to a CSV or pickle file.
    
    Returns
    -------
    geopandas.geodataframe.GeoDataFrame
        GeoDataFrame containing the storm tracks.
    """
    
    if isinstance(storms, str):
        storms = loadStorms(storms, **kwargs)
        
    if isinstance(storms, pd.DataFrame):
        # if storms is a DataFrame, convert it to a DataFrameGroupBy object
        storms = storms.groupby("ID")
    
    track_geoms = []
    for storm_ID, group in storms:
        track_geom = track(group, **kwargs)
        track_geoms.append({'ID': storm_ID, 'geometry': track_geom})
    gdf = gpd.GeoDataFrame(track_geoms, crs = kwargs.get("crs", "EPSG:4326"))
    return gdf

def track(storm, **kwargs):
    """
    Create a LineString object representing the track of a severe storm. Called by STtoolbox.tracks().
    
    Parameters
    ----------
    storm : pandas.core.frame.DataFrame
        DataFrame containing the storm data.
    
    Returns
    -------
    shapely.geometry.linestring.LineString
        LineString object representing the storm track.
    """
    x_coords, y_coords = kwargs.get("coords", ("longitude", "latitude"))
    points = [Point(x, y) for x, y in zip(storm[x_coords], storm[y_coords])]
    if len(points) == 1:
        track = points[0]
    else:
        track = LineString(points)
    return track

def saveTracks(gdf_tracks, toFile, **kwargs):
    """
    Save severe storm track data to a CSV or pickle file.
    
    Parameters
    ----------
    gdf_tracks : geopandas.geodataframe.GeoDataFrame
        DataFrame or DataFrameGroupBy containing the severe storm data.
    toFile : str
        The path to save the severe storm data.
    **kwargs : dict
        Keyword arguments specifying the format of the file.
        The valid keyword arguments are:
        - format : str
            The format of the file, either "pkl" or "csv".
        - sep : str
            The separator to use in the CSV file.
        - index : bool
            Whether to include the index in the CSV file.
    
    Returns
    -------
    None
    """
    if toFile.endswith(".pkl") or kwargs.get("format") == "pkl":
        with open(toFile, 'wb') as f:
            pickle.dump(gdf_tracks, f)
    elif toFile.endswith(".csv") or kwargs.get("format") == "csv":
        gdf_tracks.to_csv(toFile, sep = kwargs.get("sep", ","), index = kwargs.get("index", True))
    else:
        raise ValueError("Invalid file format.")
    return

def loadTracks(fromFile, **kwargs):
    """
    Load the storm tracks from a CSV or pickle file.
    
    
    
    Parameters
    ----------
    fromFile : str
        The path to the file containing the tracks.
    **kwargs : dict
        Keyword arguments specifying the format of the file.
        The valid keyword arguments are:
        - format : str
            The format of the file, either "pkl" or "csv".
        - sep : str
            The separator used in the CSV file.
        - index_col : bool
            Whether to use the first column as the index.
        - dtype : dict
            The data types of the columns.
    
    Returns
    -------
    geopandas.geodataframe.GeoDataFrame
        GeoDataFrame containing the storm tracks.
    """
    if fromFile.endswith(".pkl") or kwargs.get("format") == "pkl":
        with open(fromFile, 'rb') as f:
            gdf_tracks = pickle.load(f)
    elif fromFile.endswith(".csv") or kwargs.get("format") == "csv":
        gdf_tracks = gpd.read_csv(fromFile, sep = kwargs.get("sep", ","),
                            index_col = kwargs.get("index_col", False),
                            parse_dates = kwargs.get("parse_dates", None),
                            dtype = kwargs.get("dtype", None))
    return

def neededTimes(storms, lead_times, **kwargs):
    """
    Returns the needed datetime at which forecasts should be made by PanguWeather to be then post processed.
    
    Parameters
    ----------
    storms : pandas.core.groupby.DataFrameGroupBy or pandas.core.frame.DataFrame or str
        DataFrameGroupBy object containing storm data, or a DataFrame or a path to a CSV or pickle file.
    lead_times : list
        List of lead times to consider.
    **kwargs : dict
        Keyword arguments specifying the format of the file.
        The valid keyword arguments are:
        - time_col : str
            The column containing the time data.
        - toFile : str
            The path to save the needed times.
        - format : str
            The format of the file, either "pkl" or "csv".
    
    Returns
    -------
    pandas.core.frame.DataFrame
        DataFrame containing the needed times.
    """
    
    if isinstance(storms, str):
        storms = loadStorms(storms, **kwargs)
        
    if isinstance(storms, pd.core.groupby.DataFrameGroupBy):
        storms = storms.filter(lambda x : True)
    
    time_col = kwargs.get("time_col", "time")
    
    col = np.sort(storms[time_col].dt.floor('H').unique())
    true_col = [True]*len(col)
    res = pd.DataFrame(columns=['time'], dtype = 'datetime64[ns]')
    res.set_index('time', inplace=True)
    
    for lead_time in lead_times:
        to_add = pd.DataFrame({"time":col - lead_time, lead_time:true_col})
        to_add.set_index('time', inplace=True)
        res = pd.concat([res, to_add], axis = 1)
    
    res = res.replace({np.nan: False})
    
    toFile = kwargs.get("toFile", None)
    
    if toFile:
        if toFile.endswith(".pkl") or kwargs.get("format") == "pkl":
            with open(toFile, 'wb') as f:
                pickle.dump(res, f)
        if toFile.endswith(".csv") or kwargs.get("format") == "csv":
            pd.Series(np.array(res.index)).to_csv(toFile, index = False, header=False)
    
    return res

def nearestStorm(storms, stormsDateId, longitude, latitude, datetime, **kwargs):
    """
    Find the nearest storm to (a) given point(s) at a given time.
    
    Parameters
    ----------
    storms : pandas.core.groupby.DataFrameGroupBy or pandas.core.frame.DataFrame or str
        DataFrameGroupBy object containing storm data, or a DataFrame or a path to a CSV or pickle file.
    stormsDateId : pandas.core.frame.DataFrame or str
        DataFrame containing the dateID of the storms, or a path to a CSV or pickle file.
    longitude : np.ndarray
        The longitude of the point(s) to find the nearest storm to.
    latitude : np.ndarray
        The latitude of the point(s) to find the nearest storm to.
    datetime : pandas._libs.tslibs.timestamps.Timestamp
        The time at which to find the nearest storm.
    **kwargs : dict
        Keyword arguments specifying the format of the file.
        The valid keyword arguments are:
        - coord : str
            The CRS of the input coordinates.
        - coords : tuple
            The names of the columns containing the x and y coordinates.
    
    Returns
    -------
    str
        The ID of the nearest storm.
    np.ndarray
        The distance to the nearest storm.
    """
    
    if isinstance(storms, str):
        storms = loadStorms(storms, **kwargs)
        
    if isinstance(storms, pd.DataFrame):
        # if storms is a DataFrame, convert it to a DataFrameGroupBy object
        storms = storms.groupby("ID")
        
    if isinstance(stormsDateId, str):
        stormsDateId = loadStorms(stormsDateId, format = "pkl")
    
    from_crs = kwargs.get("coord", "WGS84")
    
    if from_crs != "LV03" and from_crs != "EPSG:21781":
        transformer = pyproj.Transformer.from_crs(from_crs, "EPSG:21781", always_xy=True)
    else:
        transformer = lambda x:x
    
    try:
        IDs = stormsDateId.loc[datetime]
    except:
        IDs = []
    dist, idm = np.ones(len(longitude))*np.inf, np.empty(len(longitude), dtype = object)
    xref, yref = transformer.transform(longitude, latitude)
    
    if isinstance(IDs, str):
        IDs = [IDs]
    
    for ID in IDs:
        storm = storms.get_group(ID)
        storm = storm[(storm["time"] >= datetime-pd.DateOffset(hours = 1)) & (storm["time"] <= datetime)]
        x_coord,y_coord = kwargs.get("coords", ("longitude", "latitude"))
        
        for x,y,a in zip(storm[x_coord], storm[y_coord], storm["A"]):
            x,y = transformer.transform(x,y)
            dist_temp = ((x-xref)**2 + (y-yref)**2)/a
            
            idm = np.where(np.greater(dist, dist_temp), ID, idm)
            dist = np.minimum(dist,dist_temp)
            
    return idm, np.sqrt(dist)/1000 #the area is in km**2
    
        
        