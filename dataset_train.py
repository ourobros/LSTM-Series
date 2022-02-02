import torch
import pywt
import numpy as np
from utils import *

def wav_den(ts_orig):
    (ca, cd) = pywt.dwt(ts_orig, 'db8')
    cat = pywt.threshold(ca, np.std(ca)/8, mode='soft')
    cdt = pywt.threshold(cd, np.std(cd)/8, mode='soft')
    ts_rec = pywt.idwt(cat, cdt, 'db8')
    return ts_rec[1:]

def get_MinMax(pair_data):
    minmax_dict = {}
    for col in pair_data.columns:
        minmax_dict[col + '_max'] = pair_data[col].max()
        minmax_dict[col + '_min'] = pair_data[col].min()
    return minmax_dict


class Pair_Dataset_Train(torch.utils.data.Dataset):
    def __init__(self, pair_data, ts_length=1, min_max_dict=None):
        self.ts_length = ts_length

        cols = ['Spread_Close', 'Spread_Open', 'Spread_High', 'Spread_Low', 'S1_volume',
                'S2_volume', 'S1_rsi', 'S2_rsi', 'S1_mfi', 'S2_mfi', 'S1_adi', 'S2_adi',
                'S1_vpt', 'S2_vpt', 'S1_atr', 'S2_atr', 'S1_bb_ma', 'S2_bb_ma', 'S1_adx',
                'S2_adx', 'S1_ema', 'S2_ema', 'S1_macd', 'S2_macd', 'S1_dlr', 'S2_dlr']


        need_drop = []
        for col in pair_data.columns:
            if col not in cols:
                need_drop.append(col)
        pair_data = pair_data.drop(columns=need_drop)
        pair_data = pair_data.fillna(0)

        # record all max,min values
        if min_max_dict is None:
            self.minmax_dict = get_MinMax(pair_data)
        else:
            self.minmax_dict = min_max_dict

        # wav transform
        wav_datas = pd.DataFrame(columns=cols)
        for col in cols:
            wav_datas[col] = wav_den(pair_data[col])
        wav_datas = MinMax_norm(wav_datas, min_max_dict)
        wav_datas = wav_datas.fillna(0)
        wav_datas = wav_datas.values

        self.datas = []
        self.labels = []

        for idx in range(wav_datas.shape[0]):
            if idx + ts_length + 1 > wav_datas.shape[0] - 1:
                break
            else:
                data = wav_datas[idx: idx + ts_length]
                labels = wav_datas[idx + ts_length, 0]

                self.datas.append(data)
                self.labels.append(labels)

    def __getitem__(self, index):
        data = torch.from_numpy(self.datas[index]).float()
        label = torch.FloatTensor([self.labels[index]])
        return data, label

    def __len__(self):
        return len(self.datas)






