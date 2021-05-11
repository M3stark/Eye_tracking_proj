#-*- coding:utf-8 -*-
"""
Plotting the NH algorithm results
@author: Zheng. Z
Written on 02.Mar.2021
"""

#%% imports
from sklearn.metrics import cohen_kappa_score

#%% function
def evaluate(gt, data):
    """
    evaluate eye movement algorithm using Cohen's Kappa
    :param gt:
    :param data:
    :return:
    """

    # Generate Ground Truth.
    _y = []
    gt_len = len(gt)
    for i in range(gt_len):
        _y.append(gt[i][4])

    # Generate data of eye movement algorithm results.
    _x = []
    for j in range(len(data)):
        if(data[j][4] == 1):
            _x.append(1)
        elif(data[j][4] == 2):
            _x.append(2)
        else:
            _x.append(3)

    print("  ---------------- Start Evaluate ----------------  ")

    # kappa
    total_kappa = cohen_kappa_score( _y, _x)
    print ('Total Kappa is %s' % total_kappa)

    # Kappa for Fixation
    k_f = cohen_kappa_score ([ i == 1 for i in _y ], [ i == 1 for i in _x ])
    print ('Kappa of Fixation is %s' % k_f)

    # Kappa for Saccade
    k_s = cohen_kappa_score ([ i == 2 for i in _y ], [ i == 2 for i in _x ])
    print ('Kappa of Saccade is %s' % k_s)

    # Kappa for PSO
    k_p = cohen_kappa_score ([ i == 3 for i in _y ], [ i == 3 for i in _x ])
    print ('Kappa of PSO is %s' % k_p)

    print (" ---------------- Evaluate Completed ----------------  ")

    return total_kappa, k_f, k_s, k_p

