import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import STtoolbox as sttb
import pickle

def durationPlot(storms, **kwargs):
    """
    Plot the duration of each storm in a DataFrameGroupBy object.
    
    Parameters
    ----------
    storms : pandas.core.groupby.DataFrameGroupBy or pandas.core.frame.DataFrame or str
        DataFrameGroupBy object containing storm data, or a DataFrame or a path to a CSV or pickle file.
    **kwargs : dict
        - toFile: str
            Path to save the plot.    
        And additional keyword arguments to pass to the loadStorms function.
        
    Returns
    -------
    matplotlib.pyplot.Figure containing the date
    """
    if isinstance(storms, str):
        storms = sttb.loadStorms(storms, **kwargs)
        
    if isinstance(storms, pd.DataFrame):
        # if storms is a DataFrame, convert it to a DataFrameGroupBy object
        storms = storms.groupby("ID")
        
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
    
    toFile = kwargs.get("toFile", None)
    if toFile:
        plt.savefig(toFile, bbox_inches = "tight")
        
    plt.show()
    plt.close()
    
    return fig

def maxAreaPlot(storms, **kwargs):
    """
    Plot the maximum area of each storm in a DataFrameGroupBy object.
    
    Parameters
    ----------
    storms : pandas.core.groupby.DataFrameGroupBy or pandas.core.frame.DataFrame or str
        DataFrameGroupBy object containing storm data, or a DataFrame or a path to a CSV or pickle file.
    **kwargs : dict
        - toFile: str
            Path to save the plot.    
        And additional keyword arguments to pass to the loadStorms function.
        
    Returns
    -------
    matplotlib.pyplot.Figure containing the date
    """
    if isinstance(storms, str):
        storms = sttb.loadStorms(storms, **kwargs)
        
    if isinstance(storms, pd.DataFrame):
        # if storms is a DataFrame, convert it to a DataFrameGroupBy object
        storms = storms.groupby("ID")
    
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
    
    toFile = kwargs.get("toFile", None)
    if toFile:
        plt.savefig(toFile, bbox_inches = "tight")
        
    plt.show()
    plt.close()
    
    return fig

def trackLengthPlot(storms, file_type, **kwargs):
    """
    Plot the track length of each storm in a DataFrameGroupBy object.
    
    Parameters
    ----------
    storms : pandas.core.groupby.DataFrameGroupBy or pandas.core.frame.DataFrame or str
        DataFrameGroupBy object containing storm data, or a DataFrame or a path to a CSV or pickle file.
    **kwargs : dict
        - toFile: str
            Path to save the plot.    
        And additional keyword arguments to pass to the loadStorms function.
        
    Returns
    -------
    matplotlib.pyplot.Figure containing the date
    """
    if file_type.lower() == "pd" or file_type.lower() == "pandas":
        storms = sttb.tracks(storms, **kwargs)
    elif file_type.lower == "gpd" or file_type.lower() == "geopandas":
        if isinstance(storms, str):
            storms = sttb.loadTracks(storms, **kwargs)
    
    lengths = storms.to_crs("EPSG:2056")["geometry"].length / 1000
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
    
    toFile = kwargs.get("toFile", None)
    if toFile:
        plt.savefig(toFile, bbox_inches = "tight")
        
    plt.show()
    plt.close()
    
    return fig

def storm_statistics_day(storms, mult, plottype = "hist", **kwargs):
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
    matplotlib.pyplot.Figure containing the date
    """
    sns.set_theme()
    
    fig, axes = plt.subplots(nrows = 5, ncols = 1, figsize = (15, 20), sharex = True)
    if isinstance(storms, str):
        storms = sttb.loadStorms(storms, **kwargs)
        
    if isinstance(storms, pd.core.groupby.DataFrameGroupBy):
        storms = storms.filter(lambda x : True)
    
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
    fig.tight_layout()
    
    toFile = kwargs.get("toFile", None)
    if toFile:
        plt.savefig(toFile, bbox_inches = "tight")
        
    plt.show()
    plt.close()    
    
    return fig

def storm_statistics_year(storms, **kwargs):
    """
    Plot the distribution of storms on a year.
    
    Returns
    -------
    matplotlib.pyplot.Figure containing the date
    """
    sns.set_theme()
    
    fig, axes = plt.subplots(nrows = 1, ncols = 1, figsize = (15, 5), sharex=True)
    if isinstance(storms, str):
        storms = sttb.loadStorms(storms, **kwargs)
        
    if isinstance(storms, pd.core.groupby.DataFrameGroupBy):
        storms = storms.filter(lambda x : True)
    
    # Plotting distribution on a year
    storms["MonthDay"] = storms["time"].dt.dayofyear
    
    sns.histplot(storms["MonthDay"], bins = np.arange(366), ax=axes)
    
    xlab = pd.date_range(start='2016-01-01', periods = 12, freq='MS')
    axes.set_xticks(xlab.dayofyear, xlab.strftime("%m-%d"))
    axes.set_xlabel("Date")
    axes.set_xlim(0, 365)
    axes.set_ylabel("Number of storms")
    axes.set_title("Distribution of storms on a year")
    fig.tight_layout()
    
    toFile = kwargs.get("toFile", None)
    if toFile:
        plt.savefig(toFile, bbox_inches = "tight")
        
    plt.show()
    plt.close()    
    
    return fig

def getStormNumber(storms = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/treated_data/Storm_tracks/CH_severe_storms_2016_2021_WGS84.pkl",
                         path = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/plots/Storm_tracks",
                         **kwargs):
    """
    Plot the number of storms that were kept after filtering.
    
    Parameters
    ----------
    storms : pandas.core.groupby.DataFrameGroupBy or str
        DataFrameGroupBy object containing the filtered storms.
    path : str
        Path to save the plot.
    **kwargs : dict
        Keyword arguments specifying the criteria used to filter the storms.
    """
    if isinstance(storms, str):
        storms = sttb.loadStorms(storms, **kwargs)
        
    if isinstance(storms, pd.DataFrame):
        storms = storms.groupby("ID")
    
    steps = kwargs.get("steps", 26)
    min_lats = np.linspace(45.49, 44.17, steps) #base on the article
    max_lats = np.linspace(47.48, 49.12, steps)
    min_lons = np.linspace(5.57, 3.60, steps)
    max_lons = np.linspace(10.29, 12.13, steps)
    res = pd.DataFrame(columns=["min_lat", "max_lat", "min_lon", "max_lon", "OR", "HS", "SHS", "RS", "SRS", "SC", "all"])
    i = 0
    for min_lat, max_lat, min_lon, max_lon in zip(min_lats, max_lats, min_lons, max_lons):
        flt = sttb.filter(storms, min_lat = min_lat, max_lat = max_lat, min_lon = min_lon, max_lon = max_lon)
        # ["w_rainstorm", "s_rainstorm", "w_hailstorm", "s_hailstorm", "supercell"]
        new_row = pd.DataFrame({"min_lat": min_lat,
                                "max_lat": max_lat,
                                "min_lon": min_lon,
                                "max_lon": max_lon,
                                "RS": len(sttb.filter(flt, storm_type = "RS")),
                                "SRS": len(sttb.filter(flt, storm_type = "SRS")),
                                "HS": len(sttb.filter(flt, storm_type = "HS")),
                                "SHS": len(sttb.filter(flt, storm_type = "SHS")),
                                "SC": len(sttb.filter(flt, storm_type = "SC")),
                                "OR": len(sttb.filter(flt, storm_type = "OR")),
                                "all": len(flt)
                                }, index = [i])
        res = pd.concat([res, new_row])
        i += 1
    
    toFile = kwargs.get("toFile", None)
    if toFile:
        res.to_csv(toFile[:-3] + "csv")
        with open(toFile[:-3] + "pkl", "wb") as file:
            pickle.dump(res, file)
        
    if kwargs.get("plot", False):
        
        sns.set_theme()
        fig, ax = plt.subplots(nrows = 2, ncols=1, figsize=(10, 12))

        df_melted = res[["OR", "RS", "SRS", "HS", "SHS", "SC"]].reset_index().melt(id_vars = 'index', var_name='Variable', value_name='Value')
        df_artificial = pd.DataFrame(columns=["Step", "Storm_type"])
        for row in df_melted.values:
            df_artificial = pd.concat([df_artificial, pd.DataFrame({"Step":[row[0]]*row[2], "Storm_type":[row[1]]*row[2]})])

        sns.histplot(df_artificial, x = 'Step', bins=steps,hue = 'Storm_type', multiple='stack', ax=ax[0])
        ax[0].set_xlabel("")
        ax[0].set_xticks([((steps-1)/5)*i+0.5 for i in range(6)], ["100%", '80%', '60%', '40%', '20%', '0%'])

        df_total = res["all"].reset_index().melt(id_vars = 'index', var_name='Variable', value_name='Value')
        df_total_artificial = pd.DataFrame(columns=["Step", "Storm_type"])
        for row in df_total.values:
            df_total_artificial = pd.concat([df_total_artificial, pd.DataFrame({"Step":[row[0]]*row[2], "Storm_type":[row[1]]*row[2]})])

        sns.histplot(df_total_artificial, x = 'Step', bins=steps,hue = 'Storm_type', multiple='stack', ax=ax[1])
        ax[1].set_xlabel("Map reduction to Switzerland only")
        ax[1].set_xticks([((steps-1)/5)*i+0.5 for i in range(6)], ["100%", '80%', '60%', '40%', '20%', '0%'])
        
        fig.suptitle("Storms to analyse depending on clipping")

        if toFile:
            fig.savefig(toFile, bbox_inches = "tight")
            
        plt.show()
        plt.close()
        
    return res
