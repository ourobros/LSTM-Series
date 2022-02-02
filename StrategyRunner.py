from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
import backtrader.analyzers as btanalyzers
import pandas as pd
import csv
import numpy as np
from margin_commission import MyCommission, zl_quote_dict
from datetime import timedelta, time
import sys
import os

symbols_dict = {
    'SHFE.rb2205': 'KQ.m@SHFE.rb',
    'SHFE.hc2205': 'KQ.m@SHFE.hc',
    'DCE.jm2205': 'KQ.m@DCE.jm',
    'DCE.j2205': 'KQ.m@DCE.j',
    'CZCE.ZC205': 'KQ.m@CZCE.ZC',
    'DCE.i2205': 'KQ.m@DCE.i',

    'DCE.a2203': 'KQ.m@DCE.a',
    'DCE.b2201': 'KQ.m@DCE.b',
    'DCE.y2205': 'KQ.m@DCE.y',
    'DCE.m2205': 'KQ.m@DCE.m',
    'CZCE.RM205': 'KQ.m@CZCE.RM',

    'DCE.l2205': 'KQ.m@DCE.l',
    'DCE.v2205': 'KQ.m@DCE.v',
    'DCE.pp2205': 'KQ.m@DCE.pp',
    'CZCE.TA205': 'KQ.m@CZCE.TA',
    'SHFE.bu2206': 'KQ.m@SHFE.bu'

}


def change_time(data, *args, **kwargs):
    dt = data.datetime.datetime(0)
    data.datetime[0] = bt.utils.date2num(dt + timedelta(minutes=1))
    return False  # length of stream is unchanged


class OptimizeRunner(object):

    def __init__(self, strategy, pair, start, end, path='', minute=1, trade_days=0, cash=300000, single=False,
                 source='tqsdk', n=15):
        self.pair = pair
        self.start = start
        self.end = end
        self.path = path
        self.minute = minute
        self.trade_days = trade_days
        self.cash = cash
        self.single = single
        self.source = source
        self.strategy = strategy
        self.n = n

    # add data source
    def add_data(self, cerebro, symbol):
        data_path = './data_day/%s_%sm.csv' % (symbol + '88', self.minute)
        dtformat = ('%Y-%m-%d %H:%M:%S')

        data = bt.feeds.GenericCSVData(
            dataname=data_path,
            datetime=0,
            open=1,
            high=2,
            low=3,
            close=4,
            volume=5,
            dtformat=dtformat,
            sessionstart=time(21, 0),
            sessionend=time(15, 0),
            fromdate=self.start,
            todate=self.end,
            timeframe=bt.TimeFrame.Minutes
        )
        if self.source == 'tqsdk':
            if self.minute == 1:
                data.addfilter(change_time)
                cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=5, name=symbol)
            else:
                cerebro.adddata(data, name=symbol)
        else:
            if self.minute == 1:
                cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=5, name=symbol)
            else:
                cerebro.adddata(data, name=symbol)

    # Set margin and commission
    def add_margin(self, cerebro):
        # Add the commission - only stocks like a for each operation
        mycomminfo_0 = MyCommission(mult=zl_quote_dict[self.pair[0]]['size'],
                                    margin_percent=zl_quote_dict[self.pair[0]]['margin_percent'])
        cerebro.broker.addcommissioninfo(mycomminfo_0, name=self.pair[0])

        mycomminfo_1 = MyCommission(mult=zl_quote_dict[self.pair[1]]['size'],
                                    margin_percent=zl_quote_dict[self.pair[1]]['margin_percent'])
        cerebro.broker.addcommissioninfo(mycomminfo_1, name=self.pair[1])

    # optimize strategy
    def runstrategy(self):
        cerebro = bt.Cerebro()
        self.add_data(cerebro, self.pair[0])
        self.add_data(cerebro, self.pair[1])

        if not os.path.exists(self.pair[0] + '88-' + self.pair[1] + '88_lstm_preds.csv'):
            print('worry')
            sys.exit()
        else:
            data_path = self.pair[0] + '88-' + self.pair[1] + '88_lstm_preds.csv'
            dtformat = ('%Y-%m-%d %H:%M:%S')
            data = bt.feeds.GenericCSVData(
                dataname=data_path,
                datetime=0,
                open=1,
                high=2,
                low=3,
                close=4,
                volume=5,
                dtformat=dtformat,
                sessionstart=time(21, 0),
                sessionend=time(15, 0),
                fromdate=self.start,
                todate=self.end,
                timeframe=bt.TimeFrame.Minutes
                )
            cerebro.adddata(data, name='preds')

        if self.single:
            # 默认参数 直接跑 (Default parameters: direct running)
            cerebro.addstrategy(self.strategy)
        else:
            # 参数优化 (parameter optimization)
            cerebro.optstrategy(self.strategy,
                                # period=range(10, 101, 10),
                                upper=np.arange(0.8, 2.1, 0.1),
                                up_medium=np.arange(0.2, 1.0, 0.1)
                                )
            cerebro.addanalyzer(btanalyzers.DrawDown, _name="drawdown")
            cerebro.addanalyzer(btanalyzers.Returns, _name="returns")
            cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='annn')

        cerebro.broker.setcash(self.cash)

        self.add_margin(cerebro)

        cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='trader')

        stratruns = cerebro.run()

        if not self.single:
            self.gen_csv_opt_result(stratruns)
            self.deal_data()

        # if self.single:
        #     cerebro.plot(numfigs=1, volume=False, zdown=False)

    def gen_csv_opt_result(self, stratruns):
        with open('opt_result_%s_%s.csv' % (self.pair[0], self.pair[1]), 'w', newline='') as f:
            writer = csv.writer(f)
            row_head = ["order", "parameter", "optimization-start", "optimization-end",
                        "opt-trading-days", "opt-trading-times", "profit", "max_draw_down"]
            writer.writerow(row_head)
            count = 0
            for stratrun in stratruns:
                for strat in stratrun:
                    count += 1
                    print('--------------------------------------------------')
                    print(strat.p._getkwargs())
                    print(strat.analyzers.drawdown.get_analysis())
                    print(strat.analyzers.returns.get_analysis())
                    print(strat.analyzers.annn.get_analysis())
                    p_dict = {}
                    for k, v in strat.p._getkwargs().items():
                        if k in ['upper', 'up_medium']:
                            v = round(v, 1)
                            p_dict[k] = v

                    drawdown_dict = {}
                    for k, v in strat.analyzers.drawdown.get_analysis().items():
                        drawdown_dict[k] = v
                    max_draw_down = drawdown_dict['max']['moneydown']
                    annn_dict = {}
                    for k, v in strat.analyzers.annn.get_analysis().items():
                        annn_dict[k] = v

                    returns_dict = {}
                    for k, v in strat.analyzers.returns.get_analysis().items():
                        returns_dict[k] = v
                    try:
                        profit_2021 = strat.analyzers.annn.get_analysis()[2021] * self.cash
                    except:
                        profit_2021 = 0
                    try:
                        profit_2022 = strat.analyzers.annn.get_analysis()[2022] * self.cash
                    except:
                        profit_2022 = 0
                    profit = profit_2021 + profit_2022
                    trading_times = int(strat.analyzers.trader.get_analysis().total.total / 2)
                    new_row = [count,
                               p_dict,
                               self.start.strftime("%Y-%m-%d"),
                               self.end.strftime("%Y-%m-%d"),
                               self.trade_days,
                               trading_times,
                               profit,
                               max_draw_down,
                               ]
                    writer.writerow(new_row)

    def deal_data(self):
        with open('choose_result_pair_trading_%s_%s.csv' % (self.pair[0], self.pair[1]), 'w', newline='') as f:
            writer = csv.writer(f)
            row_head = ["order", "futures-1", "futures-2", "parameter", "optimization-start", "optimization-end",
                        "opt-trading-days", "opt-trading-times", "profit", "max_draw_down"]
            writer.writerow(row_head)
            count = 0
            df = pd.read_csv('opt_result_%s_%s.csv' % (self.pair[0], self.pair[1]))
            df.sort_values(by='profit', ascending=False, inplace=True)
            df.drop('order', axis=1, inplace=True)
            for i in range(self.n):
                count += 1
                pair_row = [count, self.pair[0], self.pair[1], df.iloc[i]['parameter'],
                            df.iloc[i]['optimization-start'],
                            df.iloc[i]['optimization-end'],
                            df.iloc[i]['opt-trading-days'],
                            df.iloc[i]['opt-trading-times'],
                            df.iloc[i]['profit'],
                            df.iloc[i]['max_draw_down'],
                            ]
                writer.writerow(pair_row)


class BacktestRunner(object):
    def __init__(self, strategy, name, pair, start, end, path='', minute=1, trade_days=0, cash=300000, source='tqsdk',
                 n=15):
        self.name = name
        self.pair = pair
        self.start = start
        self.end = end
        self.path = path
        self.minute = minute
        self.trade_days = trade_days
        self.cash = cash
        self.source = source
        self.n = n
        self.strategy = strategy

    # add data source
    def add_data(self, cerebro, symbol):
        if self.source == 'tqsdk':
            data_path = './data_day/%s_%sm.csv' % (symbol + '88', self.minute)
            dtformat = ('%Y-%m-%d %H:%M:%S')
        else:
            data_path = './data_day/%s_%sm.csv' % (symbol + '88', self.minute)
            dtformat = ('%Y-%m-%d %H:%M:%S')
        data = bt.feeds.GenericCSVData(
            dataname=data_path,
            datetime=0,
            open=1,
            high=2,
            low=3,
            close=4,
            volume=5,
            dtformat=dtformat,
            sessionstart=time(21, 0),
            sessionend=time(15, 0),
            fromdate=self.start,
            todate=self.end,
            timeframe=bt.TimeFrame.Minutes
        )

        if self.source == 'tqsdk':
            if self.minute == 1:
                data.addfilter(change_time)
                cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=5, name=symbol)
            else:
                cerebro.adddata(data, name=symbol)
        else:
            if self.minute == 1:
                cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=5, name=symbol)
            else:
                cerebro.adddata(data, name=symbol)

    # Set margin and commission
    def add_margin(self, cerebro):
        # Add the commission - only stocks like a for each operation
        mycomminfo_0 = MyCommission(mult=zl_quote_dict[self.pair[0]]['size'],
                                    margin_percent=zl_quote_dict[self.pair[0]]['margin_percent'])
        cerebro.broker.addcommissioninfo(mycomminfo_0, name=self.pair[0])

        mycomminfo_1 = MyCommission(mult=zl_quote_dict[self.pair[1]]['size'],
                                    margin_percent=zl_quote_dict[self.pair[1]]['margin_percent'])
        cerebro.broker.addcommissioninfo(mycomminfo_1, name=self.pair[1])

    # patch backtest opt result
    def backtest(self):
        df = pd.read_csv('choose_result_pair_trading_%s_%s.csv' % (self.pair[0], self.pair[1]))
        df['%s-start' % self.name] = [self.start.strftime("%Y-%m-%d")] * self.n
        df['%s-end' % self.name] = [self.end.strftime("%Y-%m-%d")] * self.n
        df['%s-trading-days' % self.name] = [self.trade_days] * self.n
        df['%s-trading-times' % self.name] = [""] * self.n
        df['%s-profit' % self.name] = [""] * self.n
        df['%s-max-draw-down' % self.name] = [""] * self.n
        for i in range(self.n):
            p = df.iloc[i]['parameter']
            p = eval(p)
            result = self.backtest_pair_single(p)
            df.loc[i, '%s-profit' % self.name] = result['profit']
            df.loc[i, '%s-max-draw-down' % self.name] = result['max_draw_down']
            df.loc[i, '%s-trading-times' % self.name] = result['trading_times']
        df.to_csv('choose_result_pair_trading_%s_%s.csv' % (self.pair[0], self.pair[1]), index=False)

    # backtest single
    def backtest_pair_single(self, p):
        cerebro = bt.Cerebro()

        self.add_data(cerebro, self.pair[0])
        self.add_data(cerebro, self.pair[1])

        if not os.path.exists(self.pair[0] + '88-' + self.pair[1] + '88_lstm_preds.csv'):
            print('worry')
            sys.exit()
        else:
            data_path = self.pair[0] + '88-' + self.pair[1] + '88_lstm_preds.csv'
            dtformat = ('%Y-%m-%d %H:%M:%S')
            data = bt.feeds.GenericCSVData(
                dataname=data_path,
                datetime=0,
                open=1,
                high=2,
                low=3,
                close=4,
                volume=5,
                dtformat=dtformat,
                sessionstart=time(21, 0),
                sessionend=time(15, 0),
                fromdate=self.start,
                todate=self.end,
                timeframe=bt.TimeFrame.Minutes
                )
            cerebro.adddata(data, name='preds')

        cerebro.addstrategy(self.strategy, upper=round(p['upper'], 1), up_medium=round(p['up_medium'], 1))

        cerebro.addanalyzer(btanalyzers.DrawDown, _name="drawdown")
        cerebro.addanalyzer(btanalyzers.Returns, _name="returns")
        cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='annn')

        cerebro.broker.setcash(self.cash)

        self.add_margin(cerebro)

        cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='trader')
        stratruns = cerebro.run()

        drawdown_dict = {}
        for k, v in stratruns[0].analyzers.drawdown.get_analysis().items():
            drawdown_dict[k] = v

        annn_dict = {}
        for k, v in stratruns[0].analyzers.annn.get_analysis().items():
            annn_dict[k] = v

        returns_dict = {}
        for k, v in stratruns[0].analyzers.returns.get_analysis().items():
            returns_dict[k] = v
        print(stratruns[0].analyzers.annn.get_analysis())

        try:
            profit_2021 = stratruns[0].analyzers.annn.get_analysis()[2021] * self.cash
        except:
            profit_2021 = 0
        try:
            profit_2022 = stratruns[0].analyzers.annn.get_analysis()[2022] * self.cash
        except:
            profit_2022 = 0
        profit = profit_2021 + profit_2022

        result = {
            'Returns': returns_dict,
            'AnnualReturn': annn_dict,
            'DrawDown': drawdown_dict,
            'profit': profit,
            'max_draw_down': drawdown_dict["max"]['moneydown'],
            'trading_times': int(stratruns[0].analyzers.trader.get_analysis().total.total / 2)
        }

        return result
