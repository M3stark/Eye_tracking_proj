# -*- coding: utf-8 -*-

"""
    libs functions:
"""

#%% imports
import os

def split_path(fpath):
    '''Strips file extension and splits file path into directory and file name
    Parameters:
        fpath   -- full file path
    Returns:
        fdir    -- file directory
        fname   -- fine name without extension
    '''
    return os.path.split(os.path.splitext(fpath)[0])

