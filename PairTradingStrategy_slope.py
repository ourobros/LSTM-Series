
import argparse
import datetime
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
import backtrader.analyzers as btanalyzers
import pandas as pd
import csv
import numpy as np
import time
import sys
import ta
import statsmodels
import statsmodels.api as sm
from OLS import OLS_TransformationN

class PairTradingStrategyLSTM(bt.Strategy):
    params = dict(
        period=20,
        printout=True,
        upper=1.0,
        status=0,
        percent=0.7,
        up_medium=0.5,
        window_slow=30,
        window_fast=5,
    )

    def log(self, txt, dt=None):
        if self.p.printout:
            dt = dt or self.data.datetime[0]
            dt = bt.num2date(dt)
            print('%s, %s' % (dt.isoformat(), txt))

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        # 交易利润 Trading profit
        # 毛利润 Gross profit
        # 净利润 Net profit
        # print('%s 交易利润, 毛利润 %.2f, 净利润 %.2f' %
        #       (trade.data._name, trade.pnl, trade.pnlcomm))
        self.trade_times += 1

    def __init__(self):
        self.upper_limit = self.p.upper
        self.lower_limit = -self.p.upper
        self.up_medium = self.p.up_medium
        self.status = self.p.status
        self.trade_times = 0
        self.window_slow = self.p.window_slow
        self.window_fast = self.p.window_fast

        self.transform = OLS_TransformationN(self.data0, self.data1,
                                             period=self.p.period)
        self.zscore = self.transform.zscore
        self.spread = self.transform.spread
        self.slope = self.transform.slope
        self.is_stop = 0
        self.stop_future = 0


    def next(self):
        if len(self.data2.close) > self.window_slow:
            ma1 = pd.Series(self.data2.close.get(size=self.window_slow)).rolling(window=self.window_slow, center=False).mean()
            ma2 = pd.Series(self.data2.close.get(size=self.window_slow)).rolling(window=self.window_fast, center=False).mean()
            std = pd.Series(self.data2.close.get(size=self.window_slow)).rolling(window=self.window_slow, center=False).std()
            zscore = (ma2.iloc[-2] - ma1.iloc[-1]) / std.iloc[-1]

            if zscore > self.upper_limit and (self.status != 1):

                self.close(self.data0)
                self.close(self.data1)

                value = self.broker.getvalue() * self.p.percent
                comminfo_0 = self.broker.getcommissioninfo(self.data0)
                comminfo_1 = self.broker.getcommissioninfo(self.data1)
                value_x = comminfo_0.get_margin(self.data0.close)
                value_y = abs(self.slope[0]) * comminfo_1.get_margin(self.data1.close)

                percent_x = value_x / (value_x + value_y)
                percent_y = value_y / (value_x + value_y)
                real_value_x = value * percent_x
                real_value_y = value * percent_y
                x = comminfo_0.getsize(self.data0.close, real_value_x)
                y = comminfo_1.getsize(self.data1.close, real_value_y)

                self.sell(data=self.data1, size=x)
                self.buy(data=self.data0, size=y)
                self.status = 1

            elif (self.zscore[0] < self.lower_limit) and (self.status != 2):
                value = self.broker.getvalue() * self.p.percent

                comminfo_0 = self.broker.getcommissioninfo(self.data0)
                comminfo_1 = self.broker.getcommissioninfo(self.data1)
                value_x = comminfo_0.get_margin(self.data0.close)
                value_y = abs(self.slope[0]) * comminfo_1.get_margin(self.data1.close)

                percent_x = value_x / (value_x + value_y)
                percent_y = value_y / (value_x + value_y)
                real_value_x = value * percent_x
                real_value_y = value * percent_y
                x = comminfo_0.getsize(self.data0.close, real_value_x)
                y = comminfo_1.getsize(self.data1.close, real_value_y)

                self.buy(data=self.data1, size=x)
                self.sell(data=self.data0, size=y)
                self.status = 2

            elif abs(zscore) < self.up_medium:
                self.close(self.data0)
                self.close(self.data1)

    def stop(self):
        print('==================================================')
        print('Starting Value - %.2f' % self.broker.startingcash)
        print('Ending   Value - %.2f' % self.broker.getvalue())
        print('Upper {}, Lower {}, Medium {}:   '.format(self.upper_limit, self.lower_limit, self.up_medium))
        print("trade times :%s" % (int(self.trade_times / 2 + 1)))
        print('==================================================')


