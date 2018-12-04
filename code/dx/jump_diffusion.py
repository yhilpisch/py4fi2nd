#
# DX Package
#
# Simulation Class -- Jump Diffusion
#
# jump_diffusion.py
#
# Python for Finance, 2nd ed.
# (c) Dr. Yves J. Hilpisch
#
import numpy as np

from sn_random_numbers import sn_random_numbers
from simulation_class import simulation_class


class jump_diffusion(simulation_class):
    ''' Class to generate simulated paths based on
    the Merton (1976) jump diffusion model.

    Attributes
    ==========
    name: str
        name of the object
    mar_env: instance of market_environment
        market environment data for simulation
    corr: bool
        True if correlated with other model object

    Methods
    =======
    update:
        updates parameters
    generate_paths:
        returns Monte Carlo paths given the market environment
    '''

    def __init__(self, name, mar_env, corr=False):
        super(jump_diffusion, self).__init__(name, mar_env, corr)
        # additional parameters needed
        self.lamb = mar_env.get_constant('lambda')
        self.mu = mar_env.get_constant('mu')
        self.delt = mar_env.get_constant('delta')

    def update(self, initial_value=None, volatility=None, lamb=None,
               mu=None, delta=None, final_date=None):
        if initial_value is not None:
            self.initial_value = initial_value
        if volatility is not None:
            self.volatility = volatility
        if lamb is not None:
            self.lamb = lamb
        if mu is not None:
            self.mu = mu
        if delta is not None:
            self.delt = delta
        if final_date is not None:
            self.final_date = final_date
        self.instrument_values = None

    def generate_paths(self, fixed_seed=False, day_count=365.):
        if self.time_grid is None:
            # method from generic simulation class
            self.generate_time_grid()
        # number of dates for time grid
        M = len(self.time_grid)
        # number of paths
        I = self.paths
        # ndarray initialization for path simulation
        paths = np.zeros((M, I))
        # initialize first date with initial_value
        paths[0] = self.initial_value
        if self.correlated is False:
            # if not correlated, generate random numbers
            sn1 = sn_random_numbers((1, M, I),
                                    fixed_seed=fixed_seed)
        else:
            # if correlated, use random number object as provided
            # in market environment
            sn1 = self.random_numbers

        # standard normally distributed pseudorandom numbers
        # for the jump component
        sn2 = sn_random_numbers((1, M, I),
                                fixed_seed=fixed_seed)

        rj = self.lamb * (np.exp(self.mu + 0.5 * self.delt ** 2) - 1)

        short_rate = self.discount_curve.short_rate
        for t in range(1, len(self.time_grid)):
            # select the right time slice from the relevant
            # random number set
            if self.correlated is False:
                ran = sn1[t]
            else:
                # only with correlation in portfolio context
                ran = np.dot(self.cholesky_matrix, sn1[:, t, :])
                ran = ran[self.rn_set]
            dt = (self.time_grid[t] - self.time_grid[t - 1]).days / day_count
            # difference between two dates as year fraction
            poi = np.random.poisson(self.lamb * dt, I)
            # Poisson-distributed pseudorandom numbers for jump component
            paths[t] = paths[t - 1] * (
                np.exp((short_rate - rj -
                        0.5 * self.volatility ** 2) * dt +
                       self.volatility * np.sqrt(dt) * ran) +
                (np.exp(self.mu + self.delt * sn2[t]) - 1) * poi)
        self.instrument_values = paths
