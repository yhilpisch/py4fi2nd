#
# DX Package
#
# Valuation -- European Exercise Class
#
# valuation_mcs_european.py
#
# Python for Finance, 2nd ed.
# (c) Dr. Yves J. Hilpisch
#
import numpy as np

from valuation_class import valuation_class


class valuation_mcs_european(valuation_class):
    ''' Class to value European options with arbitrary payoff
    by single-factor Monte Carlo simulation.

    Methods
    =======
    generate_payoff:
        returns payoffs given the paths and the payoff function
    present_value:
        returns present value (Monte Carlo estimator)
    '''

    def generate_payoff(self, fixed_seed=False):
        '''
        Parameters
        ==========
        fixed_seed: bool
            use same/fixed seed for valuation
        '''
        try:
            # strike is optional
            strike = self.strike
        except:
            pass
        paths = self.underlying.get_instrument_values(fixed_seed=fixed_seed)
        time_grid = self.underlying.time_grid
        try:
            time_index = np.where(time_grid == self.maturity)[0]
            time_index = int(time_index)
        except:
            print('Maturity date not in time grid of underlying.')
        maturity_value = paths[time_index]
        # average value over whole path
        mean_value = np.mean(paths[:time_index], axis=0)
        # maximum value over whole path
        max_value = np.max(paths[:time_index], axis=0)
        # minimum value over whole path
        min_value = np.min(paths[:time_index], axis=0)
        try:
            payoff = eval(self.payoff_func)
            return payoff
        except:
            print('Error evaluating payoff function.')

    def present_value(self, accuracy=6, fixed_seed=False, full=False):
        '''
        Parameters
        ==========
        accuracy: int
            number of decimals in returned result
        fixed_seed: bool
            use same/fixed seed for valuation
        full: bool
            return also full 1d array of present values
        '''
        cash_flow = self.generate_payoff(fixed_seed=fixed_seed)
        discount_factor = self.discount_curve.get_discount_factors(
            (self.pricing_date, self.maturity))[0, 1]
        result = discount_factor * np.sum(cash_flow) / len(cash_flow)
        if full:
            return round(result, accuracy), discount_factor * cash_flow
        else:
            return round(result, accuracy)
