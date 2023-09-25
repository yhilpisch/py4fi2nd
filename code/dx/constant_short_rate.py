#
# DX Library
#
# Frame -- Constant Short Rate Class
#
# constant_short_rate.py
#
# Python for Finance, 2nd ed.
# (c) Dr. Yves J. Hilpisch
#
from get_year_deltas import *


class constant_short_rate(object):
    ''' Class for constant short rate discounting.

    Attributes
    ==========
    name: string
        name of the object
    short_rate: float (positive)
        constant rate for discounting

    Methods
    =======
    get_discount_factors:
        get discount factors given a list/array of datetime objects
        or year fractions
    '''

    def __init__(self, name, short_rate):
        self.name = name
        self.short_rate = short_rate
        if short_rate < 0:
            raise ValueError('Short rate negative.')
            # this is debatable given recent market realities

    def get_discount_factors(self, date_list, dtobjects=True):
        if dtobjects is True:
            dlist = get_year_deltas(date_list)
        else:
            dlist = np.array(date_list)
        dflist = np.exp(self.short_rate * -dlist)
        return np.array((date_list, dflist)).T
