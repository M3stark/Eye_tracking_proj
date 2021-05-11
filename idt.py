#-*- coding:utf-8 -*-
"""
i-dt algorithm for eye movement events detection
@author: Zheng. Z
Written on 24,Feb,2021
"""

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Identified by dispersion-based threshold algorithm
# Source: 2000-ETRA_Identifying fixations and saccades in eye-tracking protocols
# Dataset: Lund2013

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Functions
def get_window_dispersion(etdata, window_start, window_ended):
    """
    Calculate dispersion of window.
    :param etdata: eye movement data.
    :param window_start:  start of window.
    :param window_ended:  end of window.
    :return: dispersion of window.
    """
    left_x = []
    left_y = []
    for i in range(window_start, window_ended):
        left_x.append(float(etdata[i][1]))
        left_y.append(float(etdata[i][2]))

    max_x_l = max(left_x)
    max_y_l = max(left_y)
    min_x_l = min(left_x)
    min_y_l = min(left_y)
    dispersion = (max_x_l - min_x_l) + (max_y_l - min_y_l)

    # dispersion = abs(data[t-1][1] - data[t][1]) + abs(data[t-1][2] - data[t][2])
    return dispersion

def get_window_len(fs, dispersion_duration_sec_threshold):
    """
    Length of sample window for I-DT model (Minimum duration）
    :param fs: sampling frequency.
    :param dispersion_duration_sec_threshold: Length of window in sec.
    :return: window size.
    """
    return fs * dispersion_duration_sec_threshold

def get_window_parameters(etdata, current_record, window_length):
    window_start = current_record
    window_ended = window_start + window_length
    # 越界
    if(window_ended > len(etdata)):
        window_ended = len(etdata)
    window_start = int(window_start)
    window_ended = int(window_ended)

    return window_start, window_ended


def idt(etdata, dispersion_t):
    """
    i-dt algorithm for eye movement events detection
    :param etdata: eye movement data
    :param dispersion_t: dispersion threshold
    :return: eye movement events
    """
    # Counter the events
    fixation_counter = 0
    saccade_counter = 0

    fs = 500 # Sampling frequency
    dispersion_duration_sec_threshold = 0.2  # Length of window in sec.

    window_length = get_window_len(fs, dispersion_duration_sec_threshold)

    print('I-DT algorithm starts.............................')

    # Initialize counters and variables
    window_start, window_ended = get_window_parameters(etdata, 1, window_length)

    while(window_start < len(etdata)):
        dispersion = get_window_dispersion(etdata, window_start, window_ended)

        if(dispersion < dispersion_t):
            # 向窗口内添加点 直到离散度大于等于阈值
            while dispersion < dispersion_t and window_ended < len(etdata):
                window_ended += 1
                dispersion = get_window_dispersion(etdata, window_start, window_ended)

            # Now we should mark all records inside window as a fixations
            for i in range(window_start, window_ended):
                etdata[i][4] = 1
                fixation_counter += 1

            # Clear the window
            window_start, window_ended = get_window_parameters(etdata, window_ended+1, window_length)

        else:
            # According I-DT classification first record in window is a saccade.
            # So we should mark this first as saccade
            etdata[window_start][4] = 2

            if(window_start > 1):
                etdata[window_start-1][4] = 2
            saccade_counter += 1
            window_start += 1

    # Determine percentages for fixations and saccades
    total_points = saccade_counter + fixation_counter
    FIX_PER = 100 * fixation_counter / total_points
    SAC_PER = 100 * saccade_counter / total_points

    print("Total %s fixations detected" % fixation_counter)
    print("Total %s saccades detected" % saccade_counter)

    # end
    print('I-DT algorithm completed.............................')

    return etdata

