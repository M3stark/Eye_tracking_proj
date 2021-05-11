#-*- coding:utf-8 -*-
"""
i-vt algorithm for eye movement events detection
@author: Zheng. Z
Written on 23,Oct,2020
"""

############################### ivt.py ###############################
# Identified by velocity-based threshold algorithm
# Source: 2000-ETRA_Identifying fixations and saccades in eye-tracking protocols
# Dataset: Lund2013
#
#
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def ivt(data, velocity_threshold):
    """

    :param data:
    :param velocity_threshold:
    :return:
    """
    global length
    length = len(data)
    FIX_PER = 0
    SAC_PER = 0
    idx = 0
    fixation_counter = 0
    saccade_counter = 0

    print("\n ---------------- Velocity Threshold Started ---------------- ")

    for i in range(0, length-1):
        time = data[i+1][0] - data[i][0]
        distance_x = float(data[i+1][1]) - float(data[i][1])
        distance_y = float(data[i+1][2]) - float(data[i][2])
        # Euclidean distance
        distance_l = math.sqrt(math.pow(distance_x, 2) + math.pow(distance_y, 2))

        velocity = distance_l / time

        if velocity < velocity_threshold:
            # # 1 is fixation, 2 is saccade
            data[i][4] = 1
            idx = idx + 1
            fixation_counter = fixation_counter + 1
        else:
            data[i][4] = 2
            idx = idx + 1
            saccade_counter = saccade_counter + 1

    ##
    # Determine percentages for fixations and saccades
    total_points = saccade_counter + fixation_counter
    FIX_PER = 100 * fixation_counter / total_points
    SAC_PER = 100 * saccade_counter / total_points

    print("Total point numbers are: %s" % total_points)
    print("Total fixation detected are: %s, percentage is: %s" % (fixation_counter, FIX_PER))
    print("Total saccade detected are: %s, percentage is: %s" % (saccade_counter, SAC_PER))
    print (" ---------------- Velocity Threshold Completed ---------------- ")

    return  data

def fixationGroup(data):
    # fixation group
    global length
    length = len(data)
    fixation_group = []
    group_idx = 0
    for j in range(0, length - 1):
        if (data[j][4] == 2):

            if (data[j + 1][4] == 1):
                group_idx = group_idx + 1

            continue
        data[j].append(group_idx)
        fixation_group.append(data[j])

    fixation_centroids = []
    for d in range(0, group_idx):
        counter = 0
        arg_x = 0
        arg_y = 0

        for point in range(0, len(fixation_group)):
            if fixation_group[point][5] == d:
                counter = counter + 1
                arg_x = arg_x + float(fixation_group[point][1])
                arg_y = arg_y + float(fixation_group[point][2])

        arg_x = arg_x / counter
        arg_y = arg_y / counter
        _data = [arg_x, arg_y]

        fixation_centroids.append(_data)
    # print(str(idx) + " Groups detected")
    return fixation_centroids



