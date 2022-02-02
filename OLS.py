from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
from backtrader.linebuffer import LineBuffer, LinesOperation
from backtrader.indicators.basicops import PeriodN
import sys

__all__ = ['OLS_Slope_InterceptN', 'OLS_TransformationN', 'OLS_BetaN',
           'CointN']


class OLS_Slope_InterceptN(PeriodN):
    '''
    Calculates a linear regression using ``statsmodel.OLS`` (Ordinary least
    squares) of data1 on data0

    Uses ``pandas`` and ``statsmodels``
    '''
    _mindatas = 2  # ensure at least 2 data feeds are passed

    packages = (
        ('pandas', 'pd'),
        ('statsmodels.api', 'sm'),
    )
    lines = ('slope', 'intercept',)
    params = (
        ('period', 20),
    )

    def next(self):
        p0 = pd.Series(self.data0.get(size=self.p.period))
        p1 = pd.Series(self.data1.get(size=self.p.period))
        p1 = sm.add_constant(p1)
        # intercept, slope = sm.OLS(p0, p1).fit().params
        result = sm.OLS(p0, p1).fit()
        if len(result.params) == 1:
            # print(p0)
            # print(p1)
            # print(len(self.data0))
            # sys.exit()
            pass
        else:
            intercept, slope = sm.OLS(p0, p1).fit().params
            self.lines.slope[0] = slope
            self.lines.intercept[0] = intercept


class OLS_TransformationN(PeriodN):
    '''
    Calculates the ``zscore`` for data0 and data1. Although it doesn't directly
    uses any external package it relies on ``OLS_SlopeInterceptN`` which uses
    ``pandas`` and ``statsmodels``
    '''
    _mindatas = 2  # ensure at least 2 data feeds are passed
    lines = ('spread', 'spread_mean', 'spread_std', 'zscore', 'slope')
    params = (('period', 20),)

    def __init__(self):
        slint = OLS_Slope_InterceptN(*self.datas, period=self.p.period)
        spread = self.data0 - (slint.slope * self.data1 + slint.intercept)
        self.l.spread = spread

        self.l.spread_mean = bt.ind.SMA(spread, period=self.p.period)
        self.l.spread_std = bt.ind.StdDev(spread, period=self.p.period)
        self.l.zscore = (spread - self.l.spread_mean) / self.l.spread_std
        self.l.slope = slint.slope
