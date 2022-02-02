import pandas as pd
import os
import sys
import ta
import datetime
import statsmodels.api as sm 
import ta
import torch

import numpy as np

from tqdm import tqdm
from model import Pair_LSTM

import warnings
warnings.filterwarnings('ignore')
import sys
import yaml

# give data_path and pair_name, start_time and end_time, will return pair_dict
def get_datas(data_path, pair_name, start_time=None, end_time=None):

    data_close = pd.DataFrame()
    data_open = pd.DataFrame()
    data_high = pd.DataFrame()
    data_low = pd.DataFrame()
    data_volume = pd.DataFrame()

    for f1, f2, f3 in os.walk(data_path):
        for f_name in f3:
            for p_name in pair_name:
                if p_name == f_name.split('_')[0] and 'checkpoint' not in f_name:
                    df = pd.read_csv(os.path.join(data_path, f_name))
                    future_name = f_name.split('_')[0]
                    if 'datetime' not in data_close.columns:
                        data_close['datetime'] = df['datetime']
                        data_open['datetime'] = df['datetime']
                        data_high['datetime'] = df['datetime']
                        data_low['datetime'] = df['datetime']
                        data_volume['datetime'] = df['datetime']
                    data_close[future_name] = df['close']
                    data_open[future_name] = df['open']
                    data_high[future_name] = df['high']
                    data_low[future_name] = df['low']
                    data_volume[future_name] = df['volume']
    data_close['datetime'] = pd.to_datetime(data_close.datetime, format='%Y-%m-%d %H:%M:%S')
    data_open['datetime'] = pd.to_datetime(data_open.datetime, format='%Y-%m-%d %H:%M:%S')
    data_high['datetime'] = pd.to_datetime(data_high.datetime, format='%Y-%m-%d %H:%M:%S')
    data_low['datetime'] = pd.to_datetime(data_low.datetime, format='%Y-%m-%d %H:%M:%S')
    data_volume['datetime'] = pd.to_datetime(data_volume.datetime, format='%Y-%m-%d %H:%M:%S')

    if start_time is not None and end_time is not None:
        start_time = pd.to_datetime(start_time, format='%Y-%m-%d %H:%M:%S')
        end_time = pd.to_datetime(end_time, format='%Y-%m-%d %H:%M:%S')
        mask = (data_close['datetime'] >= start_time) & (data_close['datetime'] <= end_time)
        data_close = data_close.loc[mask]
        data_open = data_open.loc[mask]
        data_high = data_high.loc[mask]
        data_low = data_low.loc[mask]
        data_volume = data_volume.loc[mask]
    pair_infos = {'data_close':data_close, 'data_open': data_open, 'data_high': data_high, 'data_low':data_low, 'data_volume':data_volume}
    return pair_infos

def get_pair_datas(pair_infos, pair_name):
    data_close = pair_infos['data_close']
    data_open = pair_infos['data_open']
    data_high = pair_infos['data_high']
    data_low = pair_infos['data_low']
    data_volume = pair_infos['data_volume']

    for f_name in pair_name:
        assert f_name in data_close.columns, 'worry pair, please use get_datas first'

    pair_data = pd.DataFrame({'S1_close': data_close[pair_name[0]], 'S2_close': data_close[pair_name[1]],
                          'S1_open': data_open[pair_name[0]], 'S2_open': data_open[pair_name[1]],
                          'S1_high': data_high[pair_name[0]], 'S2_high': data_high[pair_name[1]],
                          'S1_low': data_low[pair_name[0]], 'S2_low': data_low[pair_name[1]],
                          'S1_volume': data_volume[pair_name[0]], 'S2_volume': data_volume[pair_name[1]],
                         })

    return pair_data

def get_indicators(pair_data, params, return_beginINDEX=True):

    MOMENTUM_PERIOD = params['MOMENTUM_PERIOD']
    WINDOW = params['WINDOW']
    WINDOW_FAST = params['WINDOW_FAST']
    WINDOW_SLOW = params['WINDOW_SLOW']

    if 'alpha_close' in params.keys():
        coffis = {'alpha_close': params['alpha_close'], 'alpha_open': params['alpha_open'], 'alpha_high': params['alpha_high'], 'alpha_low': params['alpha_low']}
    else:
        coffis = None

    # Relative Strength Index
    pair_data['S1_rsi'] = ta.momentum.rsi(pair_data['S1_close'], window=MOMENTUM_PERIOD)
    pair_data['S2_rsi'] = ta.momentum.rsi(pair_data['S2_close'], window=MOMENTUM_PERIOD)
    # Money Flow Index
    pair_data['S1_mfi'] = ta.volume.money_flow_index(pair_data['S1_high'], pair_data['S1_low'],
                                                     pair_data['S1_close'], pair_data['S1_volume'], window=MOMENTUM_PERIOD)
    pair_data['S2_mfi'] = ta.volume.money_flow_index(pair_data['S2_high'], pair_data['S2_low'],
                                                     pair_data['S2_close'], pair_data['S2_volume'], window=MOMENTUM_PERIOD)
    # 2. Volume Indicators
    # Accumulation/Distribution Index (ADI)
    pair_data['S1_adi'] = ta.volume.acc_dist_index(pair_data['S1_high'], pair_data['S1_low'], pair_data['S1_close'], pair_data['S1_volume'])
    pair_data['S2_adi'] = ta.volume.acc_dist_index(pair_data['S2_high'], pair_data['S2_low'], pair_data['S2_close'], pair_data['S2_volume'])
    # Volume-price trend (VPT)
    pair_data['S1_vpt'] = ta.volume.volume_price_trend(pair_data['S1_close'], pair_data['S1_volume'])
    pair_data['S2_vpt'] = ta.volume.volume_price_trend(pair_data['S2_close'], pair_data['S2_volume'])
    # 3. Volatility Indicators
    # Average True Range (ATR)
    pair_data['S1_atr'] = ta.volatility.average_true_range(pair_data['S1_high'], pair_data['S1_low'], 
                                                           pair_data['S1_close'], window=MOMENTUM_PERIOD)
    pair_data['S2_atr'] = ta.volatility.average_true_range(pair_data['S2_high'], pair_data['S2_low'], 
                                                           pair_data['S2_close'], window=MOMENTUM_PERIOD) 

    # Bollinger Bands (BB) N-period simple moving average (MA)
    pair_data['S1_bb_ma'] = ta.volatility.bollinger_mavg(pair_data['S1_close'], window=WINDOW)
    pair_data['S2_bb_ma'] = ta.volatility.bollinger_mavg(pair_data['S2_close'], window=WINDOW)

    # 4. Trend Indicators
    # Average Directional Movement Index (ADX)
    pair_data['S1_adx'] = ta.trend.adx(pair_data['S1_high'], pair_data['S1_low'], pair_data['S1_close'], window=MOMENTUM_PERIOD)
    pair_data['S2_adx'] = ta.trend.adx(pair_data['S2_high'], pair_data['S2_low'], pair_data['S2_close'], window=MOMENTUM_PERIOD)
    # Exponential Moving Average
    pair_data['S1_ema'] = ta.trend.ema_indicator(pair_data['S1_close'], window=MOMENTUM_PERIOD)
    pair_data['S2_ema'] = ta.trend.ema_indicator(pair_data['S2_close'], window=MOMENTUM_PERIOD)
    # Moving Average Convergence Divergence (MACD)
    pair_data['S1_macd'] = ta.trend.macd(pair_data['S1_close'], window_fast=WINDOW_FAST, window_slow=WINDOW_SLOW)
    pair_data['S2_macd'] = ta.trend.macd(pair_data['S2_close'], window_fast=WINDOW_FAST, window_slow=WINDOW_SLOW)

    # 5. Other Indicators
    # Daily Log Return (DLR)
    pair_data['S1_dlr'] = ta.others.daily_log_return(pair_data['S1_close'])
    pair_data['S2_dlr'] = ta.others.daily_log_return(pair_data['S2_close'])

    # 6. Spread_close 
    if coffis is None:
        est = sm.OLS(pair_data.S1_close, pair_data.S2_close)
        est = est.fit()
        alpha = -est.params[0]
    else:
        alpha = coffis['alpha_close']
    pair_data['Spread_Close'] = pair_data.S1_close + (pair_data.S2_close * alpha)
    pair_data['Spread_Close'].plot(figsize=(15,7))

    # 7.Spread_open, Spread_high, Spread_low
    if coffis is None:
        est_op = sm.OLS(pair_data.S1_open, pair_data.S2_open)
        est_op = est_op.fit()
        alpha_op = -est_op.params[0]
    else:
        alpha_op = coffis['alpha_open']
    pair_data['Spread_Open'] = pair_data.S1_open + (pair_data.S2_open * alpha_op)

    if coffis is None:
        est_hi = sm.OLS(pair_data.S1_high, pair_data.S2_high)
        est_hi = est_hi.fit()
        alpha_hi = -est_hi.params[0]
    else:
        alpha_hi = coffis['alpha_high']
    pair_data['Spread_High'] = pair_data.S1_high + (pair_data.S2_high * alpha_hi)

    if coffis is None:
        est_lo = sm.OLS(pair_data.S1_low, pair_data.S2_low)
        est_lo = est_lo.fit()
        alpha_lo = -est_lo.params[0]
    else:
        alpha_lo = coffis['alpha_low']
    pair_data['Spread_Low'] = pair_data.S1_low + (pair_data.S2_low * alpha_lo)

    if coffis is None:
        coffis = {}
        coffis['alpha_close'] = alpha
        coffis['alpha_open'] = alpha_op
        coffis['alpha_low'] = alpha_lo
        coffis['alpha_high'] = alpha_hi

    pair_data = pair_data.fillna(0)


    if return_beginINDEX:
        return pair_data[max(params.values()):], coffis
    else:
        return pair_data, coffis

def test(model, dataloader, device='cuda:0'):
    test_loss = 0
    mse_loss = torch.nn.MSELoss()
    model.eval()

    for data, label in dataloader:
        data = data.to(device)
        label = label.to(device)
        outputs = model(data)
        loss = mse_loss(outputs, label)
        test_loss += loss.item()
    return test_loss / len(dataloader)

def MinMax_norm(df, min_max_dict):
    if min_max_dict is not None:
        for col in df.columns:
            df[col] = (df[col] - min_max_dict[col + '_min']) / (min_max_dict[col + '_max'] - min_max_dict[col + '_min'])
    else: 
        for col in df.columns:
            df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
    return df


def save_predictions(checkpoint, config):
    dicts = torch.load(checkpoint)
    ts_length = dicts['ts_length']
    future1 = dicts['pair_names'][0]
    future2 = dicts['pair_names'][1]
    params = dicts['params']
    min_max_dict = dicts['minmax_dict']

    df1 = pd.read_csv(os.path.join(config['data']['data_path'], future1 + '_5m.csv'))
    df2 = pd.read_csv(os.path.join(config['data']['data_path'], future2 + '_5m.csv'))

    start_time = config['backtest']['start_time']
    end_time = config['backtest']['end_time']

    start_time = pd.to_datetime(start_time, format='%Y-%m-%d %H:%M:%S')
    end_time = pd.to_datetime(end_time, format='%Y-%m-%d %H:%M:%S')

    df_predictions = pd.DataFrame()

    df1.datetime = pd.to_datetime(df1.datetime, format='%Y-%m-%d %H:%M:%S')
    df2.datetime = pd.to_datetime(df2.datetime, format='%Y-%m-%d %H:%M:%S')

    # mask = (df1['datetime'] >= start_time) & (df1['datetime'] <= end_time)

    # df1 = df1.loc[mask]
    # df2 = df2.loc[mask]

    model = Pair_LSTM(26)
    model.load_state_dict(dicts['model'])
    model.eval()

    cols = ['Spread_Close', 'Spread_Open', 'Spread_High', 'Spread_Low', 'S1_volume',
            'S2_volume', 'S1_rsi', 'S2_rsi', 'S1_mfi', 'S2_mfi', 'S1_adi', 'S2_adi',
            'S1_vpt', 'S2_vpt', 'S1_atr', 'S2_atr', 'S1_bb_ma', 'S2_bb_ma', 'S1_adx',
            'S2_adx', 'S1_ema', 'S2_ema', 'S1_macd', 'S2_macd', 'S1_dlr', 'S2_dlr']

    begin_idx = max(params.values())

    print('-----BEGIN store PREDICTIONS-----')
    for idx in tqdm(range(df1.shape[0])):
        if idx < begin_idx or df1.iloc[idx].datetime < start_time or idx + ts_length > df1.shape[0] - 1:
            data = {'datetime': df1.iloc[idx].datetime, 
                    'close': -999, 'open': -999, 'low': -999, 'volume': -999, 
                    'high': -999, 'total_turnover': -999, 'open_interest': -999}
            df_predictions = df_predictions.append(data, ignore_index=True)
        else:
            pair_data = pd.DataFrame({'S1_close': df1[idx - begin_idx: idx + ts_length]['close'],
                                      'S2_close': df2[idx - begin_idx: idx + ts_length]['close'],
                                      'S1_open': df1[idx - begin_idx: idx + ts_length]['open'],
                                      'S2_open': df2[idx - begin_idx: idx + ts_length]['open'],
                                      'S1_high': df1[idx - begin_idx: idx + ts_length]['high'],
                                      'S2_high': df2[idx - begin_idx: idx + ts_length]['high'],
                                      'S1_low': df1[idx - begin_idx: idx + ts_length]['low'],
                                      'S2_low': df2[idx - begin_idx: idx + ts_length]['low'],
                                      'S1_volume': df1[idx - begin_idx: idx + ts_length]['volume'],
                                      'S2_volume': df2[idx - begin_idx: idx + ts_length]['volume'],
                                    })
            pair_data, alphas = get_indicators(pair_data, params, return_beginINDEX=False)
            need_drop = []
            for col in pair_data.columns:
                if col not in cols:
                    need_drop.append(col)
            pair_data.drop(columns=need_drop, inplace=True)
            pair_data = MinMax_norm(pair_data, min_max_dict)
            pair_data = pair_data[begin_idx:]
            input_data = torch.from_numpy(pair_data.values).float()
            output = model(input_data.unsqueeze(0)).view(-1)
            data2 = {'datetime': df1.iloc[idx + ts_length].datetime, 'close': output.item(), 'open': -999, 'low': -999, 
                    'volume': -999, 'high': -999, 'total_turnover': -999, 'open_interest': -999}
            df_predictions = df_predictions.append(data2, ignore_index=True)
    df_predictions = df_predictions[['datetime', 'open', 'high', 'low', 'close', 'volume', 'total_turnover', 'open_interest']] 
    df_predictions.to_csv('{}-{}_lstm_preds.csv'.format(future1, future2), index=False)