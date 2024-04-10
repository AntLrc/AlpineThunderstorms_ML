#%%

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import STtoolbox as sttb

def duration_plot(storms = sttb.get_storms(), path_to_folder = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/plots/Storm_tracks"):
    """
    Plot the duration of each storm in a DataFrameGroupBy object.
    
    Parameters
    ----------
    storms : pandas.core.groupby.DataFrameGroupBy
        DataFrameGroupBy object containing storm data.
    path_to_folder : str
        Path to the folder where the plot will be saved.
    """
    durations = []
    for name, group in storms:
        durations.append((group["time"].max() - group["time"].min()).seconds / 3600)
    quantile = np.quantile(durations, 0.95)
    
    fig, axes = plt.subplots(nrows = 2, ncols = 1)
    
    sns.histplot(durations, bins = 32, kde = True, ax=axes[0])
    axes[0].set_xlabel("Duration (hours)")
    axes[0].set_ylabel("Number of storms")
    axes[0].set_xlim(0, 11)
    axes[0].set_title("Distribution of storm durations")
    
    sns.histplot(durations, stat = 'count', cumulative=True, ax=axes[1])
    axes[1].hlines(0.95*len(durations), 0, quantile, colors='r', linestyles='dashed', label='95% quantile')
    axes[1].vlines(quantile, 0, 0.95*len(durations), colors='r', linestyles='dashed')
    axes[1].set_xticks(list(axes[1].get_xticks()) + [quantile])
    axes[1].set_yticks(list(axes[1].get_yticks()) + [0.95*len(durations)])
    axes[1].set_xlabel("Duration (hours)")
    axes[1].set_ylabel("Number of storms")
    axes[1].set_xlim(0, 11)
    axes[1].set_title("Cumulative count distribution")
    axes[1].legend(loc = 'lower right')
    
    fig.suptitle("Duration of storms")
    fig.tight_layout()
    plt.savefig(path_to_folder + "/duration_plot.png")
    plt.show()
    plt.close()
    
    return

def max_area_plot(storms = sttb.get_storms(), path_to_folder = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/plots/Storm_tracks"):
    """
    Plot the maximum area of each storm in a DataFrameGroupBy object.
    
    Parameters
    ----------
    storms : pandas.core.groupby.DataFrameGroupBy
        DataFrameGroupBy object containing storm data.
    path_to_folder : str
        Path to the folder where the plot will be saved.
    """
    areas = []
    for name, group in storms:
        areas.append(group["A"].max())
    quantile = np.quantile(areas, 0.95)
    
    
    fig, axes = plt.subplots(nrows = 2, ncols = 1)
    
    sns.histplot(areas, bins = 32, kde = True, ax=axes[0])
    axes[0].set_xlabel("Area (km^2)")
    axes[0].set_ylabel("Number of storms")
    axes[0].set_title("Distribution of storm areas")
    axes[0].set_xlim(0, 3800)
    
    sns.histplot(areas, stat = 'count', cumulative=True, ax=axes[1])
    axes[1].hlines(0.95*len(areas), 0, quantile, colors='r', linestyles='dashed', label='95% quantile')
    axes[1].vlines(quantile, 0, 0.95*len(areas), colors='r', linestyles='dashed')
    axes[1].set_xticks([0,1000,1500,2000,2500,3000,3500] + [quantile])
    axes[1].set_yticks(list(axes[1].get_yticks()) + [0.95*len(areas)])
    axes[1].legend(loc = 'lower right')
    axes[1].set_xlabel("Area (km^2)")
    axes[1].set_ylabel("Number of storms")
    axes[1].set_title("Cumulative count distribution")
    axes[1].set_xlim(0, 3800)
    
    fig.suptitle("Maximum area of storms")
    fig.tight_layout()
    plt.savefig(path_to_folder + "/max_area_plot.png")
    plt.show()
    plt.close()
    return

def track_length_plot(storms = sttb.get_storms_tracks(), path_to_folder = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/plots/Storm_tracks"):
    """
    Plot the track length of each storm in a DataFrameGroupBy object.
    
    Parameters
    ----------
    storms : geopandas.geodataframe.GeoDataFrame
        GeoDataFrame containing the storm tracks.
    path_to_folder : str
        Path to the folder where the plot will be saved.
    """
    lengths = storms["geometry"].length *2*np.pi*6371/360
    quantile = np.quantile(lengths, 0.95)
    
    fig, axes = plt.subplots(nrows = 2, ncols = 1)
    
    sns.histplot(lengths, bins = 32, kde = True, ax=axes[0])
    axes[0].set_xlabel("Track length (km)")
    axes[0].set_ylabel("Number of storms")
    axes[0].set_title("Distribution of storm track lengths")
    axes[0].set_xlim(0, 900)
    
    sns.histplot(lengths, stat = 'count', cumulative=True, ax=axes[1])
    axes[1].set_xlabel("Track length (km)")
    axes[1].set_ylabel("Number of storms")
    axes[1].set_title("Cumulative count distribution")
    axes[1].hlines(0.95*len(lengths), 0, quantile, colors='r', linestyles='dashed', label='95% quantile')
    axes[1].vlines(quantile, 0, 0.95*len(lengths), colors='r', linestyles='dashed')
    axes[1].set_xticks([0,400,600,800] + [quantile])
    axes[1].set_xlim(0, 900)
    axes[1].legend(loc = 'lower right')
    
    fig.suptitle("Track length of storms")
    fig.tight_layout()
    plt.savefig(path_to_folder + "/track_length_plot.png")
    plt.show()
    plt.close()
    return

# %%
