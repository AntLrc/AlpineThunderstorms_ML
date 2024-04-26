#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Export to hugging face repository
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
from huggingface_hub import notebook_login




LOG = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Export to hugging face repository.")

