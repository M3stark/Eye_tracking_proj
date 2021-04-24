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
from postProcessing import postProcessing
#%% load data
root = '/Users/mike/PycharmProjects/thresholdBased/etdata/lund2013_RA'
file = '%s/Lund2013_S5.npy' % root
_row = np.load(file)
row = []
data = []
for i in range(1, len(_row)):
    row = list(_row[i])
    data.append(row)
# [9.968, 726.9385, 679.0995, True, 1]


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


    print(" ---------------- Velocity Threshold Started ---------------- ")

    for i in range(0, length-1):
        time = data[i+1][0] - data[i][0]
        distance_x = float(data[i+1][1]) - float(data[i][1])
        distance_y = float(data[i+1][2]) - float(data[i][2])
        # Euclidean distance
        distance_l = math.sqrt(math.pow(distance_x, 2) + math.pow(distance_y, 2))

        velocity = distance_l / time

        if velocity < velocity_threshold:
            # # 1 is fixation, 0 is saccade
            data[i][4] = 1
            idx = idx + 1
            fixation_counter = fixation_counter + 1
        else:
            data[i][4] = 0
            idx = idx + 1
            saccade_counter = saccade_counter + 1



    ##
    # Determine percentages for fixations and saccades
    total_points = saccade_counter + fixation_counter
    FIX_PER = 100 * fixation_counter / total_points
    SAC_PER = 100 * saccade_counter / total_points

    print(" ---------------- Velocity Threshold Completed ---------------- ")
    print("Total point numbers are: %s" % total_points)
    print("Total fixation detected are: %s, percentage is: %s" % (fixation_counter, FIX_PER))
    print("Total saccade detected are: %s, percentage is: %s" % (saccade_counter, SAC_PER))


    return  data

def fixationGroup(data):
    # fixation group
    global length
    length = len(data)
    fixation_group = []
    group_idx = 0
    for j in range(0, length - 1):
        if (data[j][4] == 0):

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

VELOCITY_THRESHOLD = 520

data = ivt(data, VELOCITY_THRESHOLD)
# data = postProcessing(data)

#%% plot
plt.figure(figsize=(10,4))
plt.xlabel('time(s)')

for i in range(200, len(data)-4000):
    if(int(data[i][4]) == 1):
        plt.scatter( data[i][0], 10, s = 50, c = 'b', marker='|')
    else:
    # elif(data[i][4] == 2):
        plt.scatter( data[i][0], 10, s = 50, c = 'r', marker='|')
plt.show()


#%% save as csv file.
result_df = pd.DataFrame(data, columns = ['fname', 'sub', 'fs', 'rms', 'k'])
result_df.to_csv('%s/ivt_Lund2013_S5.csv'%root, index=False)



