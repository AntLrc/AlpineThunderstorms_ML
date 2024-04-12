import sys
sys.path.append("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/repos/SLF_dataset")

import Statistics as stt

stt.plotter(save = True, filename = "all_storms_gust_distribution.png", breakafter = 500)
