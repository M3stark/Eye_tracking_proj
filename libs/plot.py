
#-*- coding:utf-8 -*-
"""
    Plotting the eye movement events.
"""
import matplotlib.pyplot as plt


def plot_event(etdata):

    plt.figure(figsize=(10, 4))
    plt.xlabel('time(s)')
    # plt.title('Dispersion Threshold: %s' % dispersion_t)

    print('Plotting the eye movement events......................')

    for i in range(len(etdata) - 3000):
        if (int(etdata[i][4]) == 1):    # Fixation
            plt.scatter(etdata[i][0], 10, s=50, c='b', marker='|')
        elif (etdata[i][4] == 2):       # Saccade
            plt.scatter(etdata[i][0], 10, s=50, c='r', marker='|')
    plt.show()