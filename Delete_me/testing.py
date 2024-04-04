import pandas as pd
import numpy as np
import xarray as xr

path_to_file = "/home/antoine/Documents/Travail/UNIL/Preparation/Bibliographie préparatoire/Nature article + dataset/CH_severe_storms_2016_2021.csv"

xr.open_dataset(path_to_file)
xr.open_dataarray

print("ok")