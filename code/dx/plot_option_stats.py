#
# DX Package
#
# Valuation -- Plotting Options Statistics
#
# plot_option_stats.py
#
# Python for Finance, 2nd ed.
# (c) Dr. Yves J. Hilpisch
#
import matplotlib.pyplot as plt


def plot_option_stats(s_list, p_list, d_list, v_list):
    ''' Plots option prices, Deltas and Vegas for a set of
    different initial values of the underlying.

    Parameters
    ==========
    s_list: array or list
        set of initial values of the underlying
    p_list: array or list
        present values
    d_list: array or list
        results for Deltas
    v_list: array or list
        results for Vegas
    '''
    plt.figure(figsize=(10, 7))
    sub1 = plt.subplot(311)
    plt.plot(s_list, p_list, 'ro', label='present value')
    plt.plot(s_list, p_list, 'b')
    plt.legend(loc=0)
    plt.setp(sub1.get_xticklabels(), visible=False)
    sub2 = plt.subplot(312)
    plt.plot(s_list, d_list, 'go', label='Delta')
    plt.plot(s_list, d_list, 'b')
    plt.legend(loc=0)
    plt.ylim(min(d_list) - 0.1, max(d_list) + 0.1)
    plt.setp(sub2.get_xticklabels(), visible=False)
    sub3 = plt.subplot(313)
    plt.plot(s_list, v_list, 'yo', label='Vega')
    plt.plot(s_list, v_list, 'b')
    plt.xlabel('initial value of underlying')
    plt.legend(loc=0)
