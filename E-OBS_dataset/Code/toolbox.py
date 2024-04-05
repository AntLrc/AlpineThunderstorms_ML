"""
Toolbox to work with E-OBS dataset. Plotter, extractor available.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr

path_to_data = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/E-OBS_0.1-deg"



def extractor(data, date, zone = "E"):
    """Extract data from the E-OBS dataset and returns it as an xr.dataArray

    Parameters
    ----------
    data : str
        data needed, must be in ["PP", "QQ", "RR", "TG", "TN", "TX"].
    date : str
        date at which data is needed, must be formatted as "yyyy-mm-dd"
    zone : str, optional
        Europe or Switzerland where the data will be extracted, by default "E" for Europe, else "S" for Switzerland.

    Returns
    -------
    xr.dataArray
        Data from the E-OBS dataset at date.
    """    
    if not data in ["PP", "QQ", "RR", "TG", "TN", "TX"]:
        raise ValueError('Invalid data. Argument data must be in ["PP", "QQ", "RR", "TG", "TN", "TX"].')
    if len(date) != 10 or date[4] != '-' or date[7] != '-' or not (date[:4].isdigit() and date[5:7].isdigit() and date[8:].isdigit()) or int(date[:4]) < 2011 or int(date[:4]) > 2023 or int(date[5:7]) > 12:
        raise ValueError('Invalid date. Argument date must be formatted as "yyyy-mm-dd" between 2011-01-01 and 2023-12-12')
    if not zone in ["E", "S"]:
        raise ValueError('Invalid zone argument. If provided, argument zone must be in ["E", "S"] which stand for Europe and Switzerland')
    
    path_to_file = path_to_data + '/' + data + '/' + data.lower() + "_ens_mean_0.1deg_reg_2011-2023_v29.0e.nc"
    da = xr.open_dataarray(path_to_file)
    try:
        res = da.sel(time = date)
    except:
        raise ValueError('Invalid date. Argument date must be formatted as "yyyy-mm-dd" between 2011-01-01 and 2023-12-12') #only reason why could have not been opened
    if zone == "S":
        return res.loc[45.75:47.95, 5.95:10.55]
    else:
        return res
    
def plotter(data, date, zone = "E", path_to_folder = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/plots/E-OBS_dataset"):
    """Plot data from the E-OBS dataset.

    Parameters
    ----------
    data : str
        data needed, must be in ["PP", "QQ", "RR", "TG", "TN", "TX"].
    date : str
        date at which data is needed, must be formatted as "yyyy-mm-dd"
    zone : str, optional
        Europe or Switzerland where the data will be extracted, by default "E" for Europe, else "S" for Switzerland.
    path_to_folder : str, optional
        dir to which data should be saved, by default "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/repos/E-OBS_dataset/Results"
    """
    da = extractor(data, date, zone = zone)
    da.plot()
    plt.show()
    try:
        plt.savefig(path_to_folder + '/' + date + "_" + data + "_" + zone + ".png")
    except:
        raise ValueError("path_to_folder should be formatted as path/to/folder")
    return    



