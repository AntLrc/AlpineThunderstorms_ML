import pandas as pd
import geopandas as gpd
import xarray as xr


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
    res["time"] = df["time"].apply(lambda x : x[0:4] + '-' + x[4:6] + '-' + x[6:8] + 'T' + x[8:10] + ':' + x[10:12]+":00")

    res.to_csv("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/CH_severe_storms_2016_2021_WGS84.csv", index = False)

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
    path = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/CH_severe_storms_2016_2021_WGS84.csv"
    try:
        df = pd.read_csv(path, dtype = {"ID" : str}, parse_dates=["time"])
    except FileNotFoundError:
        raise FileNotFoundError("CSV file not found.")  
    
    storms1 = df.loc[(df["time"].dt.date >= pd.to_datetime(date).date()) & (df["time"].dt.date < pd.to_datetime(date).date() + pd.Timedelta(days=1))].groupby("ID")
    
    return storms1

to_WGS()

