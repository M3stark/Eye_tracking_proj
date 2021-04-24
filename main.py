#-*- coding:utf-8 -*-
"""
Threshold-based algorithm for eye movement events detection
@author: Zheng. Z
Written on 23,Oct,2020
"""

############################### main.py ###############################
# Threshold-based threshold algorithm
# Source: 2000-ETRA_Identifying fixations and saccades in eye-tracking protocols
# Dataset: Lund2013
#
#

#%% imports
import os, json, glob
from distutils.dir_util import mkpath
from tqdm import tqdm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from libs.functions import split_path
from idt import idt, plot_event


# ——————————————————————————————————————————————————————
def covert(data,geom):
    """
    covert x, y in degrees to x, y in pixels
    :param data: x, y in degrees
    :param geom: 'display_width_pix' value and 'display_height_pix' value
    :return: x, y in pixels
    """
    for i in range(len(data)):
        _x = data[i][1] * 37.1099172728 + geom['display_width_pix'] / 2
        _y = data[i][2] * 37.1099172728 + geom['display_height_pix'] / 2
        data[i][1] = _x
        data[i][2] = _y
# ——————————————————————————————————————————————————————



#%% load files
root = '/Users/mike/PycharmProjects/thresholdBased/etdata'
# dataset = '%s/lund2013_RA' % root
dataset = '%s/MFD_500' % root
# exp_output = '%s/res_IDT' % root
exp_output = '%s/500_rank' % root
# Create a directory if 'exp_output' is not exist
if not (os.path.exists(exp_output)):
    mkpath(exp_output)

#load config
with open('config.json', 'r') as f:
    config = json.load(f)

with open('%s/db_config.json' % dataset, 'r') as f:
    db_config = json.load(f)
    config['geom'] = db_config['geom']

# for i-vt algorithm
#TODO


FILES = sorted(glob.glob('%s/*.npy' % dataset))

# Dispersion Threshold, maybe needed to change
# DISPERSION_THRESHOLD = 64
DISPERSION_THRESHOLD = 60

for file in tqdm(FILES[:]):
    # file name
    fdir, fname = split_path(file)

    # for eacjh file
    _row = np.load(file)

    # tuple to list
    row = list(list(items) for items in list(_row))

    # Coordinate conversion
    covert(row, db_config['geom'])
    # print(row)

    # call idt
    etdata = idt(row, DISPERSION_THRESHOLD)

    # print(etdata)

    # plot_event(etdata)

    # %% save as csv file.
    result_df = pd.DataFrame(etdata, columns = ['timestamp', 'x_pos', 'y_pos', 'sub', 'events'])
    result_df.to_csv('%s/idt_%s.csv' % (exp_output, fname), index=False)




