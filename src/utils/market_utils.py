#!/usr/bin/env python # coding: utf-8
def find_closet_tick(price):
    '''
    Given some price, this returnds the 'nearest' Betfair price
    Note : 0.5 will round down
    '''
    
    import numpy as np
    
    ticks = np.concatenate([np.arange(1.01, 2.01, 0.01),
                            np.arange(2.02, 3.02, 0.02),
                            np.arange(3.05, 4.05, 0.05),
                            np.arange(4.1, 6.1, 0.1),
                            np.arange(6.2, 10.2, 0.2),
                            np.arange(10.5, 20.5, 0.5),
                            np.arange(21, 31, 1),
                            np.arange(32, 52, 2),
                            np.arange(55, 105, 5),
                            np.arange(110, 1010, 10)])
    
    idx = (np.abs(ticks - price)).argmin() 
    
    return round(ticks[idx], 2) 