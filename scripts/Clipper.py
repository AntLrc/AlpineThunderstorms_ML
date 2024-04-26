#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clipper to Switzerland to prepare for the post processing.
"""

# Not tested yet

import pickle
import cdsapi
import argparse
import pandas as pd
import subprocess
import numpy as np
import os
import utils
import subprocess
import logging

LOG = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Clip a file to Switzerland.")

parser.add_argument("--input", "-i",
                    type=str,
                    help="Path to the input file, without the end '_LT.nc' or '_ST.nc'.")

parser.add_argument("--output", "-o",
                    type=str,
                    help="Path to the output file.")

parser.add_argument("--in-place",
                    action="store_true",
                    help="Overwrite the input file.")

parser.add_argument("--latmin",
                    type=float,
                    help="Minimum latitude at which to clip.")

parser.add_argument("--latmax",
                    type=float,
                    help="Maximum latitude at which to clip.")

parser.add_argument("--lonmin",
                    type=float,
                    help="Minimum longitude at which to clip.")

parser.add_argument("--lonmax",
                    type=float,
                    help="Maximum longitude at which to clip.")

args = parser.parse_args()

LOG.info(f"Clipping file {args.input} to Switzerland...")

utils.clip_file(args.input, args.latmin, args.latmax, args.lonmin, args.lonmax, output_path=args.output if not args.in_place else None)

if args.in_place:
    LOG.info(f"Clipped file saved to {args.input}.")
else:
    LOG.info(f"Clipped file saved to {args.output}.")


