def main():
    import os, sys
    dev_path = os.path.dirname(__file__)
    src_path = os.path.join(dev_path, "..", 'src')
    sys.path.append(src_path)
    print(src_path, flush = True)

    import linReg.Statistics as lrstat

    import argparse

    parser = argparse.ArgumentParser(description='Interpolate PW outputs over SMN stations.')

    parser.add_argument("--data-vars",
                        type=str,
                        nargs='+',
                        default="all",
                        help="List of data variables to load.")

    parser.add_argument("--dirname-stations",
                        type=str,
                        help="The directory to load station data from.")

    parser.add_argument("--dirname-pangu-weather",
                        type=str,
                        help="The directory to load PW output data from.")

    parser.add_argument("--minyear",
                        type=int,
                        default=2016,
                        help="The minimum year to load data from.")

    parser.add_argument("--maxyear",
                        type=int,
                        default=2021,
                        help="The maximum year to load data from.")

    parser.add_argument("--minmonth",
                        type=int,
                        default=4,
                        help="The minimum month to load data from.")

    parser.add_argument("--maxmonth",
                        type=int,
                        default=10,
                        help="The maximum month to load data from.")

    parser.add_argument("--storm-file",
                        type=str,
                        default=None,
                        help="The file to load storm data from.")

    parser.add_argument("--storm-date-id-file",
                        type=str,
                        default=None,
                        help="The file to load storm date IDs from.")

    parser.add_argument("--coord",
                        type=str,
                        default="WGS84",
                        help="The CRS of the storm data coordinates.")

    parser.add_argument("--coords",
                        type=str,
                        nargs='+',
                        default=["longitude", "latitude"],
                        help="The names of the columns containing the storm data coordinates.")

    parser.add_argument("--from-file",
                        type=str,
                        default=None,
                        help="The file to load data from.")

    parser.add_argument("--to-file",
                        type=str,
                        help="The file to save data to. If dirpath is provided, this is the name of the file.")

    parser.add_argument("--dirpath",
                        type=str,
                        default=None,
                        help="The directory to save data to.")

    args = parser.parse_args()

    print("Loading data with lrstat.loadData...", flush=True)
    data = lrstat.loadData(dataVars=args.data_vars,
                    dirnameStations=args.dirname_stations,
                    dirnamePW=args.dirname_pangu_weather,
                    minyear=args.minyear,
                    maxyear=args.maxyear,
                    minmonth=args.minmonth,
                    maxmonth=args.maxmonth,
                    stormFile=args.storm_file,
                    stormDateIDFile=args.storm_date_id_file,
                    coord=args.coord,
                    coords=args.coords,
                    fromFile=args.from_file)

    print("Saving data with lrstat.saveData...", flush=True)
    lrstat.saveData(data, args.to_file, dirpath = args.dirpath)
    
if __name__ == "__main__":
    main()