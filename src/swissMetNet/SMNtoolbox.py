import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os
import sys
from sklearn.cluster import KMeans, SpectralClustering
from sklearn import metrics
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.img_tiles as cimgt


def loadData(data_vars, dirname, **kwargs):
    """
    Load data from a directory.
    
    Parameters
    ----------
    data_vars : str
        The type of data to load, either 'precip', 'wind gust' or 'all'.
    dirname : str
        The directory to load data from.
    **kwargs : dict
        Additional keyword arguments.
        These can include:
            minyear : int
                The minimum year to load data from.
            maxyear : int
                The maximum year to load data from.
            minmonth : int
                The minimum month to load data from.
            maxmonth : int
                The maximum month to load data from.
            stations : list
                A list of stations to load data from.
    """
    data_vars = ["precipitation_amount"]*(data_vars == "precip" or data_vars == "all") + ["wind_speed_of_gust"]*(data_vars == "wind gust" or data_vars == "all")
    if len(data_vars) == 0:
        raise ValueError("Invalid data type, data must be in 'precip', 'wind gust' or 'all'.")
    
    minyear = kwargs.get('minyear', 2016)
    maxyear = kwargs.get('maxyear', 2024)
    minmonth = kwargs.get('minmonth', 1)
    maxmonth = kwargs.get('maxmonth', 12 if maxyear != 2024 else 3)
    stations = kwargs.get('stations', "all")
    if not(isinstance(stations, list)) and stations != "all":
        raise ValueError("Invalid stations type, stations must be a list of stations or 'all'.")
    files = filesForDates(dirname, pd.to_datetime(f"{minyear}-{minmonth}"), pd.to_datetime(f"{maxyear}-{maxmonth}"))
    res = None
    for file in files:
        print(file)
        data = xr.open_dataset(os.path.join(dirname,file), engine = "netcdf4")
        data = data[data_vars]
        if stations != "all":
            data = data.where(data["station"].isin(stations), drop = True)
        if res is None:
            res = data
        else:
            res = xr.concat([res, data], dim = "time")
    
    return res
        
def filesForDates(dirname, mindate, maxdate):
    """
    Get all files in a directory that are in a given date range.
    
    Parameters
    ----------
    dirname : str
        The directory to search.
    mindate : datetime
        The minimum date.
    maxdate : datetime
        The maximum date.
    
    Returns
    -------
    list
        A list of files in the directory that are in the given date range.
    """
    files = os.listdir(dirname)
    files = [f for f in files if f.endswith(".nc")]
    files = [f for f in files if pd.to_datetime(f"{f[-9:-5]}-{f[-5:-3]}") >= mindate and pd.to_datetime(f"{f[-9:-5]}-{f[-5:-3]}") <= maxdate]
    files.sort()
    return files

def KMeansStationClustering(data, statistics, **kwargs):
    """
    Cluster data based on a set of statistics provided as functions with K-Means algorithm.
    
    Parameters
    ----------
    data : xarray.Dataset
        The data to cluster.
    statistics : list
        A list of (function_name, function) to apply to the data.
    
    Returns
    """
    measures = [stat[1](data) for stat in statistics]
    stations = data.station.values
    result = xr.Dataset(
        data_vars = dict([ (statistics[i][0], measures[i] ) for i in range(len(statistics)) ]),
        coords = {"station":data.station,
                  "longitude":data.longitude,
                  "latitude":data.latitude
                  }
    )
    result = result.dropna(dim = "station", how = "any")
    X = np.array([result[stat[0]] for stat in statistics]).T
    kmeans = KMeans(n_clusters = kwargs.get("n_clusters", 2)).fit(X)
    
    result["label"] = xr.DataArray(kmeans.labels_, coords = {"station":result.station}, dims = ["station"])
    return result, metrics.silhouette_score(X, kmeans.labels_, metric='euclidean')

def SpectralStationClustering(data, **kwargs):
    """
    Cluster data based on correlation between station, aggregated over time, with Spectral Clustering algorithm.
    """
    stations = data.station.values
    nb_of_stations = len(stations)
    if "affinities" in kwargs.keys():
        affinities = kwargs.get("affinities")
    else:
        affinities = np.array([[xr.corr(data.isel(station=i), data.isel(station=j), dim = "time").values for i in range(nb_of_stations)] for j in range(nb_of_stations)])
    affinities = np.abs(affinities) if kwargs.get("method", "abs") == "abs" else affinities
    nans = np.isnan(np.diag(affinities))
    nansmatrix = nans.reshape((-1,1))@nans.reshape((1,-1))
    affinities = affinities[~nans][:,~nans]
    np.nan_to_num(affinities, copy = False, nan=0.)
    result = xr.Dataset(
        data_vars = {"affinity":(["station", "station"], affinities)},
        coords = {"station":("station",data.station.values[~nans]),
                  "longitude":("station",data.longitude.values[~nans]),
                  "latitude":("station",data.latitude.values[~nans])
                  }
    )
    clustering = SpectralClustering(n_clusters = kwargs.get("n_clusters", 2), assign_labels='discretize', affinity = 'precomputed').fit(affinities)
    result["label"] = xr.DataArray(clustering.labels_, coords = {"station":result.station}, dims = ["station"])
    distances = np.clip(-np.log(affinities), a_min = 0, a_max = 1e8)
    np.nan_to_num(distances, copy = False, nan=1e8)
    return result, metrics.silhouette_score(distances, clustering.labels_, metric='precomputed')


def plotStations(longitude, latitude, labels = None, **kwargs):
    
    google_tiles = cimgt.GoogleTiles(style='satellite')
    n_clusters = kwargs.get("clusters", None)
    if isinstance(n_clusters, list):
        silh = kwargs.get("silhouette_score")
        title = kwargs.get("title", None)
        fig = plt.figure(figsize = ((len(n_clusters)//3 + 1)*5, 15))
        fig.tight_layout()
        fig.suptitle("SwissMetNet stations" if title is None else title, fontsize = 30)
        gs = GridSpec(nrows = len(n_clusters)//3 + 1, ncols = 3)
        for i in range(len(n_clusters)):
            ax = fig.add_subplot(gs[i//3, i%3], projection=google_tiles.crs)
            ax.add_feature(cfeature.BORDERS)
            ax.set_extent([5.8, 10.5, 45.8, 47.8], crs=ccrs.PlateCarree())
            ax.add_image(google_tiles, 9)

            color = labels[i]
            ax.scatter(longitude, latitude, transform=ccrs.PlateCarree(), marker = kwargs.get("marker", "X"), c = color, zorder = 3, cmap = 'inferno')
            ax.gridlines(draw_labels=True, auto_inline=True)
            ax.xaxis.set_label_position('top')
            # add a box around the following annotation
            ax.legend([f"n_clusters = {n_clusters[i]}"]).set_zorder(10)
            
        
        ax = fig.add_subplot(gs[-1, :])
        ax.plot(n_clusters, silh, 'rx-')
        ax.set_xlabel("n_clusters")
        ax.set_ylabel("Silhouette score")

        if kwargs.get("toFile", None):
            fig.savefig(kwargs.get("toFile", None), bbox_inches='tight')
        if kwargs.get("show", False):
            plt.show()
            plt.close()
        
    else:
        fig, ax = plt.subplots(subplot_kw={'projection': google_tiles.crs})
        ax.set_extent([5.8, 10.5, 45.8, 47.8], crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.BORDERS)
        ax.add_image(google_tiles, 9)

        color = 'darkred' if labels is None else labels
        ax.scatter(longitude, latitude, transform=ccrs.PlateCarree(), marker = '+', c = color, zorder = 3, cmap = 'inferno')
        ax.gridlines(draw_labels=True, auto_inline=True)
        ax.xaxis.set_label_position('top')
        title = kwargs.get("title", None)
        ax.set_title("SwissMetNet stations" if title is None else title)

        if kwargs.get("toFile", None):
            fig.savefig(kwargs.get("toFile", None), bbox_inches='tight')
        if kwargs.get("show", False):
            plt.show()
            plt.close()
    return fig, ax