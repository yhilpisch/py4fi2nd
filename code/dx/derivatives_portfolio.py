#
# DX Package
#
# Portfolio -- Derivations Portfolio Class
#
# derivatives_portfolio.py
#
# Python for Finance, 2nd ed.
# (c) Dr. Yves J. Hilpisch
#
import numpy as np
import pandas as pd

from dx_valuation import *

# models available for risk factor modeling
models = {'gbm': geometric_brownian_motion,
          'jd': jump_diffusion,
          'srd': square_root_diffusion}

# allowed exercise types
otypes = {'European': valuation_mcs_european,
          'American': valuation_mcs_american}


class derivatives_portfolio(object):
    ''' Class for modeling and valuing portfolios of derivatives positions.

    Attributes
    ==========
    name: str
        name of the object
    positions: dict
        dictionary of positions (instances of derivatives_position class)
    val_env: market_environment
        market environment for the valuation
    assets: dict
        dictionary of market environments for the assets
    correlations: list
        correlations between assets
    fixed_seed: bool
        flag for fixed random number generator seed

    Methods
    =======
    get_positions:
        prints information about the single portfolio positions
    get_statistics:
        returns a pandas DataFrame object with portfolio statistics
    '''

    def __init__(self, name, positions, val_env, assets,
                 correlations=None, fixed_seed=False):
        self.name = name
        self.positions = positions
        self.val_env = val_env
        self.assets = assets
        self.underlyings = set()
        self.correlations = correlations
        self.time_grid = None
        self.underlying_objects = {}
        self.valuation_objects = {}
        self.fixed_seed = fixed_seed
        self.special_dates = []
        for pos in self.positions:
            # determine earliest starting_date
            self.val_env.constants['starting_date'] = \
                min(self.val_env.constants['starting_date'],
                    positions[pos].mar_env.pricing_date)
            # determine latest date of relevance
            self.val_env.constants['final_date'] = \
                max(self.val_env.constants['final_date'],
                    positions[pos].mar_env.constants['maturity'])
            # collect all underlyings and
            # add to set (avoids redundancy)
            self.underlyings.add(positions[pos].underlying)

        # generate general time grid
        start = self.val_env.constants['starting_date']
        end = self.val_env.constants['final_date']
        time_grid = pd.date_range(start=start, end=end,
                                  freq=self.val_env.constants['frequency']
                                  ).to_pydatetime()
        time_grid = list(time_grid)
        for pos in self.positions:
            maturity_date = positions[pos].mar_env.constants['maturity']
            if maturity_date not in time_grid:
                time_grid.insert(0, maturity_date)
                self.special_dates.append(maturity_date)
        if start not in time_grid:
            time_grid.insert(0, start)
        if end not in time_grid:
            time_grid.append(end)
        # delete duplicate entries
        time_grid = list(set(time_grid))
        # sort dates in time_grid
        time_grid.sort()
        self.time_grid = np.array(time_grid)
        self.val_env.add_list('time_grid', self.time_grid)

        if correlations is not None:
            # take care of correlations
            ul_list = sorted(self.underlyings)
            correlation_matrix = np.zeros((len(ul_list), len(ul_list)))
            np.fill_diagonal(correlation_matrix, 1.0)
            correlation_matrix = pd.DataFrame(correlation_matrix,
                                              index=ul_list, columns=ul_list)
            for i, j, corr in correlations:
                corr = min(corr, 0.999999999999)
                # fill correlation matrix
                correlation_matrix.loc[i, j] = corr
                correlation_matrix.loc[j, i] = corr
            # determine Cholesky matrix
            cholesky_matrix = np.linalg.cholesky(np.array(correlation_matrix))

            # dictionary with index positions for the
            # slice of the random number array to be used by
            # respective underlying
            rn_set = {asset: ul_list.index(asset)
                      for asset in self.underlyings}

            # random numbers array, to be used by
            # all underlyings (if correlations exist)
            random_numbers = sn_random_numbers((len(rn_set),
                                                len(self.time_grid),
                                                self.val_env.constants['paths']),
                                               fixed_seed=self.fixed_seed)

            # add all to valuation environment that is
            # to be shared with every underlying
            self.val_env.add_list('cholesky_matrix', cholesky_matrix)
            self.val_env.add_list('random_numbers', random_numbers)
            self.val_env.add_list('rn_set', rn_set)

        for asset in self.underlyings:
            # select market environment of asset
            mar_env = self.assets[asset]
            # add valuation environment to market environment
            mar_env.add_environment(val_env)
            # select right simulation class
            model = models[mar_env.constants['model']]
            # instantiate simulation object
            if correlations is not None:
                self.underlying_objects[asset] = model(asset, mar_env,
                                                       corr=True)
            else:
                self.underlying_objects[asset] = model(asset, mar_env,
                                                       corr=False)

        for pos in positions:
            # select right valuation class (European, American)
            val_class = otypes[positions[pos].otype]
            # pick market environment and add valuation environment
            mar_env = positions[pos].mar_env
            mar_env.add_environment(self.val_env)
            # instantiate valuation class
            self.valuation_objects[pos] = \
                val_class(name=positions[pos].name,
                          mar_env=mar_env,
                          underlying=self.underlying_objects[
                    positions[pos].underlying],
                payoff_func=positions[pos].payoff_func)

    def get_positions(self):
        ''' Convenience method to get information about
        all derivatives positions in a portfolio. '''
        for pos in self.positions:
            bar = '\n' + 50 * '-'
            print(bar)
            self.positions[pos].get_info()
            print(bar)

    def get_statistics(self, fixed_seed=False):
        ''' Provides portfolio statistics. '''
        res_list = []
        # iterate over all positions in portfolio
        for pos, value in self.valuation_objects.items():
            p = self.positions[pos]
            pv = value.present_value(fixed_seed=fixed_seed)
            res_list.append([
                p.name,
                p.quantity,
                # calculate all present values for the single instruments
                pv,
                value.currency,
                # single instrument value times quantity
                pv * p.quantity,
                # calculate Delta of position
                value.delta() * p.quantity,
                # calculate Vega of position
                value.vega() * p.quantity,
            ])
        # generate a pandas DataFrame object with all results
        res_df = pd.DataFrame(res_list,
                              columns=['name', 'quant.', 'value', 'curr.',
                                       'pos_value', 'pos_delta', 'pos_vega'])
        return res_df
