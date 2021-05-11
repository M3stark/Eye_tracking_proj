#-*- coding:utf-8 -*-
"""
Threshold-based algorithm for eye movement events detection
@author: Zheng. Z
Written on 23,Oct,2020
"""

""" 
    ##############################################################
    #           Threshold-based threshold algorithms.            #
    #                                                            #
    #   updates:                                                 #
    #   > I-DT                                                   #     
    #   > I-VT                                                   #
    #   > I-VDT                                                  #
    #                                                            #
    #   Dataset: Lund2013 (on Angular coordinates)               #
    ############################################################## 
"""


#%% imports
import os, json, glob
import copy
from distutils.dir_util import mkpath
from tqdm import tqdm
import numpy as np
import pandas as pd
from libs.functions import split_path
from libs.evaluate import evaluate
from idt import idt
from ivt import ivt
import ivdt
from libs.plot import plot_event

#%% Function
# ——————————————————————————————————————————————————————#
def covert(data,geom):
    """
    covert x, y in __degrees__ to x, y in __pixels__
    :param data: x, y in degrees
    :param geom: 'display_width_pix' value and 'display_height_pix' value
    :return: x, y in pixels
    """
    for i in range(len(data)):
        _x = data[i][1] * 37.1099172728 + geom['display_width_pix'] / 2
        _y = data[i][2] * 37.1099172728 + geom['display_height_pix'] / 2
        data[i][1] = _x
        data[i][2] = _y
# ——————————————————————————————————————————————————————#


#%% load files
# ——————————————————————————————————————————————————————#
root = '/Users/mike/PycharmProjects/thresholdBased/etdata'
# dataset = '%s/lund2013_angle' % root
dataset = '%s/test' % root
# dataset = '%s/MFD_500' % root
exp_output = '%s/rank_kappa' % root
# exp_output = '%s/500_rank' % root

# Create a directory if 'exp_output' is not exist
if not (os.path.exists(exp_output)):
    mkpath(exp_output)

#load config
with open('config.json', 'r') as f:
    config = json.load(f)

with open('%s/db_config.json' % dataset, 'r') as f:
    db_config = json.load(f)
    config['geom'] = db_config['geom']

FILES = sorted(glob.glob('%s/*.npy' % dataset))
# ——————————————————————————————————————————————————————#

#%% Set params.
# ——————————————————————————————————————————————————————#
# I-DT param.                                           #
# Dispersion Threshold, maybe needed to change.         #
# ——————————————————————————————————————————————————————#
DISPERSION_THRESHOLD = 50

# ——————————————————————————————————————————————————————#
# I-VT param.                                           #
# ——————————————————————————————————————————————————————#
VELOCITY_THRESHOLD = 70

# ——————————————————————————————————————————————————————#
# I-VDT param.                                          #
# ——————————————————————————————————————————————————————#
SACCADE_DETECTION_THRESHOLD = 7     # deg
IDT_DISPERSION_THRESHOLD = 1.35     # deg
IDT_WINDOW_LENGTH = 0.1             # 0.1s -> 100 ms
MINIMAL_SACCADE_AMPLITUDE = 4       # deg
MINIMAL_SACCADE_LENGTH = 4          # samples
SAMPLE_RATE = 500
delta_t_sec = 1 / SAMPLE_RATE

# declare a ivdt object.
ivdt = ivdt.IVDT(SACCADE_DETECTION_THRESHOLD,
                 IDT_DISPERSION_THRESHOLD,
                 IDT_WINDOW_LENGTH,
                 MINIMAL_SACCADE_AMPLITUDE,
                 MINIMAL_SACCADE_LENGTH)
# ——————————————————————————————————————————————————————#


#%% Start detect...
for file in tqdm(FILES[:]):
    # file name
    fdir, fname = split_path(file)

    # for each file
    _row = np.load(file)

    # Ground Truth
    row = list(list(items) for items in list(_row))

    # deep copy and clear the events
    data = copy.deepcopy (row)

    for i in range(len(data)):
        data[i][4] = 0


    """
        Notes:
        > In I-DT algorithm, the data we used is in __pixels__,
          so if the row data is in __degrees__, may need to call "covert" function.
        > In I-VDT algorithm and I-VT algorithm, the data we used is in __degrees__.
    """

    print(" \n================ Now working on %s ================ " % fname)
    # Coordinate conversion
    #covert(data, db_config['geom'])

    # I-DT
    # ------------------------------------------------ #
    #etdata = idt(data, DISPERSION_THRESHOLD)
    # ------------------------------------------------ #

    # print(etdata)

    # I-VT
    # ------------------------------------------------ #
    etdata = ivt(data, VELOCITY_THRESHOLD, delta_t_sec)
    # ------------------------------------------------ #

    # I-VDT
    # ------------------------------------------------ #
    #etdata = ivdt.classify(data, delta_t_sec)
    # ------------------------------------------------ #

    # plot the event
    # plot_event(etdata)

    # evaluate
    evaluate(row, etdata)

    # %% save as csv file.
    #result_df = pd.DataFrame(etdata, columns = ['timestamp', 'x_pos', 'y_pos', 'sub', 'events'])

    # select a path to save res.
    #result_df.to_csv('%s/idt_%s.csv' % (exp_output, fname), index=False)       # idt
    #result_df.to_csv('%s/ivt_%s.csv' % (exp_output, fname), index=False)       # ivt
    #result_df.to_csv('%s/ivdt_%s.csv' % (exp_output, fname), index=False)      # ivdt

    print (" ================ %s worked. ================ \n" % fname)
