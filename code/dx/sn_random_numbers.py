#
# DX Package
#
# Frame -- Random Number Generation
#
# sn_random_numbers.py
#
# Python for Finance, 2nd ed.
# (c) Dr. Yves J. Hilpisch
#
import numpy as np


def sn_random_numbers(shape, antithetic=True, moment_matching=True,
                      fixed_seed=False):
    ''' Returns an ndarray object of shape shape with (pseudo)random numbers
    that are standard normally distributed.

    Parameters
    ==========
    shape: tuple (o, n, m)
        generation of array with shape (o, n, m)
    antithetic: Boolean
        generation of antithetic variates
    moment_matching: Boolean
        matching of first and second moments
    fixed_seed: Boolean
        flag to fix the seed

    Results
    =======
    ran: (o, n, m) array of (pseudo)random numbers
    '''
    if fixed_seed:
        np.random.seed(1000)
    if antithetic:
        ran = np.random.standard_normal(
            (shape[0], shape[1], shape[2] // 2))
        ran = np.concatenate((ran, -ran), axis=2)
    else:
        ran = np.random.standard_normal(shape)
    if moment_matching:
        ran = ran - np.mean(ran)
        ran = ran / np.std(ran)
    if shape[0] == 1:
        return ran[0]
    else:
        return ran
