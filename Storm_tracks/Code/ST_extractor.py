import pandas as pd
import geopandas as gpd


def to_WGS():
    path = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/severe_storms_2016-2021/CH_severe_storms_2016_2021.csv"

    df = pd.read_csv(path, sep = ';')
    gdf = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df.chx,df.chy), crs = "EPSG:2056")
    gdf_wgs = gdf.to_crs("EPSG:4326")
    wgsx = []
    wgsy = []

    for p in gdf_wgs.geometry:
        x,y = p.coords[0]
        wgsx.append(x)
        wgsy.append(y)

    df_wgs = df
    res = df_wgs.drop(["chx","chy"],axis = 1)
    res["longitude"] = wgsx
    res["latitude"] = wgsy

    res.to_csv("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/CH_severe_storms_2016_2021_WGS84.csv")


