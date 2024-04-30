import xarray as xr
import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description='Test for corrupted netcdf files in given directory')
    
    parser.add_argument("--dirpath", "-d",
                        type = str,
                        help = "Path to directory containing well-organised subdirectories of netcdf files.")
    
    parser.add_argument("--year", "-y",
                        type = str,
                        help = "Year to verify for files, format YYYY.")
    
    parser.add_argument("--month", "-m",
                        type = str,
                        help = "Month to verify for files, format mm.")
    
    parser.add_argument("--remove", "-r",
                        action = "store_true",
                        help = "Remove corrupted files.")
    
    parser.add_argument("--remove-index", "-i",
                        action = "store_true",
                        help = "Remove index of corrupted files.")
    
    parser.add_argument("--file-type", "-f",
                        type=str,
                        help="Type of file to verify.")
    
    args = parser.parse_args()
    year = args.year
    month = args.month
    dirpath = args.dirpath
    remove = args.remove
    remove_index = args.remove_index
    file_type = args.file_type
    
    folderpath = os.path.join(dirpath, year, month)
    files = [file for file in os.listdir(folderpath) if file.endswith(file_type)]
    files.sort()
    
    nothing = True
    for file in files:
        try:
            xr.open_dataset(os.path.join(folderpath, file))
            print(f"File {file} is not corrupted.")
        except:
            print(f"\t/!\\ Corrupted file: {file}")
            if remove:
                print(f"\t\tRemoving {file}...")
                os.remove(os.path.join(folderpath, file))
            if remove_index:
                print(f"\t\tRemoving index of {file}...")
                os.remove(os.path.join(folderpath, file + "*.idx"))
            nothing = False
    
    if nothing:
        print("No corrupted files found.")
    
    

if __name__ == '__main__':
    main()