import torch
import pywt
import numpy as np
from utils import *

import warnings
from tqdm import tqdm
warnings.filterwarnings('ignore')

class Pair_Dataset_Test(torch.utils.data.Dataset):
    def __init__(self, pair_data, params, ts_length=1, min_max_dict=None):
        self.ts_length = ts_length

        cols = ['Spread_Close', 'Spread_Open', 'Spread_High', 'Spread_Low', 'S1_volume',
                'S2_volume', 'S1_rsi', 'S2_rsi', 'S1_mfi', 'S2_mfi', 'S1_adi', 'S2_adi',
                'S1_vpt', 'S2_vpt', 'S1_atr', 'S2_atr', 'S1_bb_ma', 'S2_bb_ma', 'S1_adx',
                'S2_adx', 'S1_ema', 'S2_ema', 'S1_macd', 'S2_macd', 'S1_dlr', 'S2_dlr']

        self.datas = []
        self.labels = []

        begin_index = max(params.values())

        print('------BEGIN CRATE TEST_DATASET-----')
        for idx in tqdm(range(pair_data.shape[0])):
            if idx + ts_length > pair_data.shape[0] - 1:
                break
            if idx < begin_index:
                continue
            else:
                df_tmp = pair_data[idx - begin_index: idx + ts_length]
                df_tmp, coffis = get_indicators(df_tmp, params, return_beginINDEX=False)
                need_drop = []
                for col in df_tmp.columns:
                    if col not in cols:
                        need_drop.append(col)
                df_tmp.drop(columns=need_drop, inplace=True)
                df_tmp = MinMax_norm(df_tmp, min_max_dict)
                self.datas.append(df_tmp[begin_index:].fillna(0).values)
                label_row = pair_data.iloc[idx + ts_length]
                org_label = label_row['S1_close'] + label_row['S2_close'] * coffis['alpha_close']
                label = (org_label - min_max_dict['Spread_Close_min']) / (min_max_dict['Spread_Close_max'] - min_max_dict['Spread_Close_min'])
                self.labels.append(label)

    def __getitem__(self, index):
        data = torch.from_numpy(self.datas[index]).float()
        label = torch.FloatTensor([self.labels[index]])
        return data, label

    def __len__(self):
        return len(self.datas)