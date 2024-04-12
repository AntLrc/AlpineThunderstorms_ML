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

def storm_statistics_day(mult, plottype = "hist"):
    """
    Plot the distribution of storms on a day.
    
    Parameters
    ----------
    mult : str
        Method for multiple plots.
    plottype : str
        Type of plot to use.
    
    Returns
    -------
    None
    """
    sns.set_theme()
    
    fig, axes = plt.subplots(nrows = 5, ncols = 1, figsize = (15, 20), sharex = True)
    storms = pd.read_csv("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/Storm_tracks/CH_severe_storms_2016_2021.csv", parse_dates=["time"])
    
    plt.tight_layout()
    
    # Plotting distribution on a day
    storms["MoD"] = storms["time"].dt.hour*60 + storms["time"].dt.minute
    sns.histplot(storms["MoD"], bins = 12*24, ax=axes[0])
    # Getting all hour - 5min in a day
    xlab = pd.date_range(start='2016-01-01', periods = 24, freq='2h')
    axes[0].set_xticks(xlab.hour*60 + xlab.minute, xlab.strftime("%H:%M"))
    axes[0].set_xlabel("Time of the day")
    axes[0].set_xlim(0, 24*60)
    axes[0].set_ylabel("Number of storms")
    
    # Plotting distribution on a day per month
    three_months = [[],
                    ["January", "February", "March"],
                    ["April", "May", "June"],
                    ["July", "August", "September"],
                    ["October", "November", "December"]]
    for i in range(1, 5):
        storms["MoD"] = storms["time"].dt.hour*60 + storms["time"].dt.minute
        storms["Month"] = storms["time"].dt.month_name()
        if not (storms[storms["Month"].isin(three_months[i])].empty):
            if plottype == "hist":
                sns.histplot(data = storms[storms["Month"].isin(three_months[i])],
                             x="MoD", bins = 12*24,
                             ax=axes[i],
                             hue = "Month",
                             multiple=mult)
                axes[i].set_ylim(0,700)
            elif plottype == "kde":
                sns.kdeplot(data = storms[storms["Month"].isin(three_months[i])],
                            x="MoD",
                            ax=axes[i],
                            hue = "Month",
                            multiple=mult)
        # Getting all hour - 5min in a day
        xlab = pd.date_range(start='2016-01-01', periods = 24, freq='2h')
        axes[i].set_xticks(xlab.hour*60 + xlab.minute, xlab.strftime("%H:%M"))
        axes[i].set_xlim(0, 24*60)
        axes[i].set_ylabel("Number of storms")
    
    axes[-1].set_xlabel("Time of the day")
    fig.suptitle("Distribution of storms on a day")
    
    
    
    plt.show()
    plt.close()
    
    
    
    return

def storm_statistics_year():
    """
    Plot the distribution of storms on a year.
    
    Returns
    -------
    None
    """
    sns.set_theme()
    
    fig, axes = plt.subplots(nrows = 1, ncols = 1, figsize = (15, 5), sharex=True)
    storms = pd.read_csv("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/Storm_tracks/CH_severe_storms_2016_2021.csv", parse_dates=["time"])
    
    plt.tight_layout()
    
    # Plotting distribution on a year
    storms["MonthDay"] = storms["time"].dt.dayofyear
    
    sns.histplot(storms["MonthDay"], bins = np.arange(366), ax=axes)
    
    xlab = pd.date_range(start='2016-01-01', periods = 12, freq='MS')
    axes.set_xticks(xlab.dayofyear, xlab.strftime("%m-%d"))
    axes.set_xlabel("Date")
    axes.set_xlim(0, 365)
    axes.set_ylabel("Number of storms")
    axes.set_title("Distribution of storms on a year")

# %%
