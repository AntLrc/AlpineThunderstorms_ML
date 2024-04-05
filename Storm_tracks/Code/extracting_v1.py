import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr

path = "/work/FAC/FGSE/IDYST/tbeucler/downscaling/raw_data/severe_storms_2016-2021/CH_severe_storms_2016_2021.csv"

df = pd.read_csv(path, sep = ';')

# Group the data by storm ID
grouped = df.groupby('ID')


# Plot each storm track
count = 0
for name, group in grouped:
    if count <= 4:
        plt.plot(group['chx'], group['chy'], label=f'Storm {name}')
        count +=1
    else:
        break

# Add labels and title
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Storm Tracks')
plt.legend()
plt.grid(True)
plt.savefig("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/repos/Storm_tracks/Results/figureTest.png")

