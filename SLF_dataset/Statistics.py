#%%

import pandas as pd
import pickle
import numpy as np
import geopandas as gpd
import xarray as xr
import seaborn as sns
from shapely.geometry import LineString, Point
import matplotlib.pyplot as plt

import sys
sys.path.append("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/repos/Storm_tracks")
sys.path.append("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/repos/SLF_dataset")

import SLFtoolbox as slftb
import STtoolbox as sttb

sns.set_theme()

def test():
    print("Hello world!")

def get_wind_gust(stations = slftb.get_stations(),
                   sampling = True,
                   samplesize = 100,
                   plotter = False,
                   save = False,
                   filename = "wind_gust_distribution.png"):
    """
    Plot the distribution of wind gust.
    
    Parameters
    ----------
    gdf : geopandas.geodataframe.GeoDataFrame
        The station data.
    sampling : bool
        If True, take a random sample of 100 (by default) data points for each station.
    samplesize : int
        The number of data points to sample for each station.
    plotter : bool
        If True, plot the distribution.
    save : bool
        If True, save the plot.
    filename : str
        The name of the file to save the plot.
    Returns
    -------
    numpy.ndarray
        Array containing the wind gust data.
    """
    data = np.array([], dtype = float)
    
    for id in stations["station_code"]:
        heads = pd.read_csv("/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/SLF_dataset/measurement-data.slf.ch/imis/data/by_station/"+ id + ".csv", nrows=0)
        if "VW_30MIN_MAX" in heads.columns: # Check if the column exists
            df = pd.read_csv("/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/SLF_dataset/measurement-data.slf.ch/imis/data/by_station/"+ id + ".csv",
                             usecols=["VW_30MIN_MAX"])
            if sampling:
                indexes = np.random.randint(0,df.size,samplesize)
                sample = df.loc[indexes,"VW_30MIN_MAX"].values
            else:
                sample = df["VW_30MIN_MAX"].values
            data = np.concatenate((data, sample[~np.isnan(sample)]))
    
    if plotter:
        sns.histplot(data, binwidth= 1., kde=True)
        plt.xlabel("Wind speed [m/s]")
        plt.xlim(0, 50)
        plt.ylabel("Count")
        plt.title("Distribution of wind gust")
        
        
        if save:
            plt.savefig("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/plots/SLF_dataset/"+filename)
        plt.show()
        plt.close()    
    return data

def get_storm_gust(storm, stations = slftb.get_stations()):
    """
    Plot the distribution of wind gust during a specific storm.
    
    Parameters
    ----------
    storm : pandas.core.frame.DataFrame
        DataFrame containing the storm data.
    gdf : geopandas.geodataframe.GeoDataFrame
        The station data.
    
    Returns
    -------
    numpy.ndarray
        Array containing the wind gust data.
    """
    data = np.array([], dtype = float)
    for i in storm.index:
        station_codes = slftb.station_nearby(Point(storm["longitude"][i], storm["latitude"][i]), np.sqrt(storm["A"][i]), stations)
        for station_code in station_codes:
            heads = pd.read_csv("/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/SLF_dataset/measurement-data.slf.ch/imis/data/by_station/"+ station_code + ".csv", nrows=0)
            if "VW_30MIN_MAX" in heads.columns and "measure_date" in heads.columns:
                df = pd.read_csv("/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/SLF_dataset/measurement-data.slf.ch/imis/data/by_station/"+ station_code + ".csv",
                                 usecols=["measure_date", "VW_30MIN_MAX"], parse_dates=["measure_date"])
                gust = df.loc[(df["measure_date"] > storm["time"][i]) & (df["measure_date"] <= storm["time"][i] + pd.Timedelta(minutes=30)), "VW_30MIN_MAX"].values
                data = np.concatenate((data, gust))
    return data

def get_storms_gust(storms = sttb.get_storms(),
                     stations = slftb.get_stations(),
                     plotter = False,
                     save = False,
                     filename = "storms_gust_distribution.png",
                     breakafter = 50,
                     stormtype = ""):
    """
    Plot the distribution of wind gust during severe storms.
    
    Parameters
    ----------
    storms : pandas.core.groupby.DataFrameGroupBy
        DataFrameGroupBy object containing storm data.
    stations : geopandas.geodataframe.GeoDataFrame
        The station data.
    save : bool
        If True, save the plot.
    filename : str
        The name of the file to save the plot.
    breakafter : int
        The number of wind gust values to collect before stopping.
    stormtype : str
        The type of storm to plot. If empty, all storms will be plotted.
    
    Returns
    -------
    data : numpy.ndarray
        Array containing the wind gust data.
    """
    st_type = (stormtype == "RS")*"w_rainstorm" + (stormtype == "SRS")*"s_rainstorm" + (stormtype == "HS")*"w_hailstorm" + (stormtype == "SHS")*"s_hailstorm" + (stormtype == "SC")*"supercell"

    
    data = np.array([], dtype = float)
    i = 0
    tot = len(storms)
    names = list(storms.groups.keys())
    while len(data) < breakafter: # Stop if the number of wind gust values collected is greater than breakafter
        indice = np.random.randint(0, len(names))
        storm = storms.get_group(names[indice])
        name = names.pop(indice)
        if stormtype == "OR" and (1 in storm[["w_rainstorm", "s_rainstorm", "w_hailstorm", "s_hailstorm", "supercell"]].values[0]): # Check if the storm is of the right type
            continue
        elif stormtype != "" and stormtype != "OR" and storm[st_type].values[0] != 1: # Check if the storm is of the right type
            continue
        print("\rProcessing storm " + name + ". " + str(i) + " storms processed out of " + str(tot) + ". Data contains " + str(len(data)) + " values.", end="")
        data = np.concatenate((data, get_storm_gust(storm, stations)))
        names.pop(indice)
        i += 1
    
    print("\n"+ str(i) +" storms have been processed. Data contains " + str(len(data)) + " values.")
    
    if plotter:
        print("\nPlotting histogram...")
        sns.histplot(data, binwidth= 1., kde=True)
        plt.xlabel("Wind speed [m/s]")
        plt.xlim(0, 50)
        plt.ylabel("Count")
        plt.title("Distribution of wind gust during " + stormtype + " storms")

        if save:
            plt.savefig("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/plots/SLF_dataset/"+filename)
        plt.show()
        plt.close()
    return data


def plotter(save = False,
            filename = "all_storms_gust_distribution.png",
            breakafter = 100,
            savedata = False,
            dataname = "data_gust.pkl"):
    """
    Plot the distributions of wind gust during severe storms.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    data : dict
        Dictionary containing the wind gust data for each storm type.
    """
    types = ["WS","OR", "RS", "SRS", "HS", "SHS", "SC"]
    print("Processing general wind gusts...")
    data = {"WS": get_wind_gust(samplesize = breakafter)}
    for stormtype in types:
        if stormtype == "WS":
            continue
        print("Processing " + stormtype + " storms...")
        data[stormtype] = get_storms_gust(stormtype = stormtype, breakafter = breakafter)
    fig, axes = plt.subplots(nrows = 7, ncols = 1, figsize = (21, 29.7), sharex='all')
    plt.tight_layout()
    
    for i in range(7):
        sns.histplot(data[types[i]], binwidth= 1., kde=True, ax = axes[i])
        axes[i].set_xlabel("Wind speed [m/s]")
        axes[i].set_xlim(0, 60)
        axes[i].set_ylabel("Count")
        if i == 0:
            axes[i].set_title("General distribution of wind gust")
        else:
            axes[i].set_title("Distribution of wind gust during " + types[i] + " storms")
    
    if save:   
        plt.savefig("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/plots/SLF_dataset/" + filename)
        with open("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/plots/SLF_dataset/data_gust.pkl","wb") as handle:
            pickle.dump(data, handle)
    plt.show()
    plt.close()
    return data


# %%

