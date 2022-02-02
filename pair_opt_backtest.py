# coding: utf-8
# ##################################################################
# Pair Trading adapted to backtrader
# with PD.OLS and info for StatsModel.API
# author: Remi Roche
##################################################################

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import arrow
from PairTradingStrategy import PairTradingStrategyLSTM
from tqsdk import TqApi, TqAuth
from StrategyRunner import OptimizeRunner, BacktestRunner

if __name__ == '__main__':
    """
    10+5(中间周期优化+后周期回测)
    以profit作为目标 优化结果取前15个 ，优化周期profit需要都为正，后周期回测利润为正
    """
    path = '/home/ourobros/add_test/data_day'
    minute = 5
    source = 'rqdata'  # tqsdk,rqdata
    cash = 300000
    n = 15
    now = arrow.get('2022-01-28T15:00:00Z')
    start = now.shift(weeks=-15, days=0).floor('day')
    end = now.shift(weeks=-5).ceil('day')
    print('start', start)
    print("end", end)
    api = TqApi(auth=TqAuth("oiwio", "T7c-7MmCHMRFo9Kkbb-.A"))
    d = api.get_trading_calendar(start.date(), end.date())
    d = d[d.trading]
    print(d.shape[0])
    opt_trade_days = d.shape[0]

    start_2 = now.shift(weeks=-5, days=0).floor('day')
    end_2 = now.shift(weeks=0).ceil('day')
    print('start_2', start_2)
    print("end_2", end_2)
    d = api.get_trading_calendar(start_2.date(), end_2.date())
    d = d[d.trading]
    print(d.shape[0])
    after_trade_days = d.shape[0]

    api.close()

    pairs = [
        # 黑色系 Black series
        # ('SHFE.ag', 'SHFE.pb')
        # ('DCE.b', 'DCE.j')
        # ('DCE.a', 'CZCE.TA')
        # ('SHFE.rb', 'SHFE.hc')
        # ('DCE.l', 'CZCE.OI')
        ('DCE.jm', 'CZCE.SM')
    ]

    # 优化 optimize
    for pair in pairs:
        opt_runner = OptimizeRunner(PairTradingStrategyLSTM, pair, start, end, path, minute, opt_trade_days,
                                    cash, False,
                                    source, n)

        opt_runner.runstrategy()
        print("%s %s 配对 完成优化" % (pair[0], pair[1]))

    # 后周期回测 patch backtest
    name = "After-cycle-backtest"
    for pair in pairs:
        bactest_runner = BacktestRunner(PairTradingStrategyLSTM, name, pair, start_2, end_2, path, minute,
                                        after_trade_days,
                                        cash, source, n)
        bactest_runner.backtest()
        print("%s %s 配对 完成后周期回测" % (pair[0], pair[1]))

    # 验证某个交易对回测
    # name = "verify"
    # from datetime import datetime
    # from TestStrategy import TestStrategy
    #
    # # after_trade_days = 0
    # # start_2 = datetime(2022, 1, 17, 10, 0, 0)
    # # end_2 = datetime(2022, 1, 17, 21, 25, 0)
    # # end_2 = now.shift(weeks=0).ceil('day')
    # print(start_2)
    # print(end_2)
    # p = {'period': 10, 'upper': 1.9, 'up_medium': 0.2}
    # pair = ('SHFE.rb2205', 'SHFE.hc2205')
    # bactest_runner = BacktestRunner(PairTradingStrategyNew_spread3, name, pair, start_2, end_2, path, minute,
    #                                 after_trade_days,
    #                                 cash, source, n)
    # # 单独回测某个参数
    # bactest_runner.backtest_pair_single(p)
