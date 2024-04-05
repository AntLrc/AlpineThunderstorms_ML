import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import geopandas as gpd

df1 = pd.read_csv("/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/severe_storms_2016-2021/CH_severe_storms_2016_2021.csv", sep = ';', dtype={'ID':'string', 'chx':'string', 'chy':'string', 'time':'string'})
df = df1[["ID", "time"]]

gdf = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df1.chx,df1.chy), crs = "EPSG:2056")

gdf_wgs = gdf.to_crs("EPSG:4326")

print(gdf_wgs)