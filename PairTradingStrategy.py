
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

class PairTradingStrategyLSTM(bt.Strategy):
    params = dict(
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

    def next(self):
        if len(self.data.datetime) < 10:
            print('datetime: ', bt.num2date(self.datetime[0]))
            print(self.data0.close[0])
            print(self.data1.close[0])
            print(self.data2.close[0])



        if len(self.data2.close) > self.window_slow:
            ma1 = pd.Series(self.data2.close.get(size=self.window_slow)).rolling(window=self.window_slow, center=False).mean()
            ma2 = pd.Series(self.data2.close.get(size=self.window_slow)).rolling(window=self.window_fast, center=False).mean()
            std = pd.Series(self.data2.close.get(size=self.window_slow)).rolling(window=self.window_slow, center=False).std()
            zscore = (ma2.iloc[-2] - ma1.iloc[-1]) / std.iloc[-1]

            if zscore > self.upper_limit and (self.status != 1):

                self.close(self.data0)
                self.close(self.data1)

                value = 0.5 * self.broker.getvalue() * 0.7
                print("当前每个品种可用资产", value)
                comminfo_0 = self.broker.getcommissioninfo(self.data0)
                x = comminfo_0.getsize(self.data0.close, value)
                x = max(1, x)
                comminfo_1 = self.broker.getcommissioninfo(self.data1)
                y = comminfo_1.getsize(self.data1.close, value)
                y = max(1, y)
                self.sell(data=self.data1, size=x)
                self.buy(data=self.data0, size=y)
                self.status = 1
                
            elif zscore < self.lower_limit and (self.status != 2):

                self.close(self.data0)
                self.close(self.data1)

                value = 0.5 * self.broker.getvalue() * 0.7
                # print("当前每个品种可用资产", value)
                comminfo_0 = self.broker.getcommissioninfo(self.data0)
                x = comminfo_0.getsize(self.data0.close, value)
                x = max(1, x)
                comminfo_1 = self.broker.getcommissioninfo(self.data1)
                y = comminfo_1.getsize(self.data1.close, value)
                y = max(1, y)

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


