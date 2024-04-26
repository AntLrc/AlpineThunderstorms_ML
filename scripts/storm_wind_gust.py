import argparse
import sys

sys.path.append("/work/FAC/FGSE/IDYST/tbeucler/downscaling/alecler1/repos/src/SLF_dataset")

import Statistics as stt

class CustomAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values.lower() == 'true':
            setattr(namespace, self.dest, True)
        elif values.lower() == 'false':
            setattr(namespace, self.dest, False)
        else:
            parser.error("Invalid value for --save argument. Use 'true' or 'false'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot wind gust distribution')
    parser.add_argument('--save', action=CustomAction, help='whether to save the plot', default=False)
    parser.add_argument('--filename', type=str, help='name of the file to save the plot', default="all_storms_gust_distribution.png")
    parser.add_argument('--breakafter', type=int, help='number of wind gust values to collect before stopping for each storm', default=100)
    parser.add_argument('--savedata', action=CustomAction, help='whether to save the data', default=False)
    parser.add_argument('--dataname', type=str, help='name of the file to save the data', default="data_gust.pkl")
    
    args = parser.parse_args()
    save, filename, breakafter, savedata, dataname = args.save, args.filename, args.breakafter, args.savedata, args.dataname
    
    print("Statistics.plotter running with the following arguments:")
    print("save: ", save)
    if save:
        print("filename: ", filename)
    print("breakafter: ", breakafter)
    print("savedata: ", savedata)
    if savedata:
        print("dataname: ", dataname)
    
    stt.plotter(save, filename, breakafter, savedata, dataname)