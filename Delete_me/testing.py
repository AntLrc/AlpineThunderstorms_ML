import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

path_to_file = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/E-OBS_0.1-deg/RR/rr_ens_mean_0.1deg_reg_2011-2023_v29.0e.nc"

da = xr.open_dataarray(path_to_file)

da.sel(time = "2019-08-01").plot()
plt.show()
plt.savefig("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/repos/E-OBS_dataset/Results/rr_ens_mean_0.1deg_reg_2011-2023_v29.0e.png")

print("ok")