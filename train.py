import numpy as np
import pandas as pd
import ta
import sys
from datetime import datetime
from tqdm import tqdm
import torch

from model import Pair_LSTM
# from dataset import Pair_Dataset
# from dataset_test import Pair_Dataset_Test
from utils import *
import yaml

# read config
# with open('config.yaml', encoding='utf-8') as f:
#     config = f.read()

# print(config)
# sys.exit()


# parameters for training
data_path = data_path = '/home/ourobros/add_test/data_day/'
# 2020-01-02 09:05:00 - 2022-01-19 14:40:00
pair_name = ['SHFE.ag88', 'SHFE.pb88']
params = {'MOMENTUM_PERIOD': 30, 'WINDOW': 30, 'WINDOW_FAST': 30, 'WINDOW_SLOW': 60}
ts_length = 1
epochs = 50
device = 'cuda:0'

# use 3/4 data to train, last data for test
tmp_df = pd.read_csv(os.path.join(data_path, pair_name[0] + '_5m.csv'))
length_tmp_df = tmp_df.shape[0]
train_start = str(tmp_df.datetime[0])
train_end = str(tmp_df.datetime[int(length_tmp_df * 0.75)])

test_start = str(tmp_df.datetime[int(length_tmp_df * 0.75) + 1])
test_end = str(tmp_df.datetime[length_tmp_df - 1])

pair_data = get_datas(data_path=data_path, pair_name=pair_name, start_time=train_start, end_time=train_end)

train_pair_infos = get_datas(data_path=data_path, pair_name=pair_name, start_time=train_start, end_time=train_end)
train_pair_data = get_pair_datas(train_pair_infos, pair_name)
train_pair_data, coffis = get_indicators(train_pair_data, params, return_beginINDEX=True)
params.update(coffis)
print(params)

train_dataset = Pair_Dataset(train_pair_data, ts_length=ts_length)

print(len(train_dataset))
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=32, shuffle=True)

test_pair_infos = get_datas(data_path=data_path, pair_name=pair_name, start_time=test_start, end_time=test_end)
test_pair_data = get_pair_datas(test_pair_infos, pair_name)
test_dataset = Pair_Dataset_Test(test_pair_data, params, ts_length, train_dataset.minmax_dict)
print(len(test_dataset))
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=32, shuffle=False)

model = Pair_LSTM(train_dataset[0][0].shape[1])
model = model.to(device)
loss_func = torch.nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

best_test_loss = 10000
for epoch in range(epochs):
    test_loss = test(model, test_loader)
    if test_loss < best_test_loss:
        best_test_loss = test_loss
        dicts = {'pair_names':pair_name, 'params': params, 'model':model.state_dict(), 'minmax_dict': train_dataset.minmax_dict, 'ts_length': ts_length}
        torch.save(dicts, '{}-{}-lstm2.pth'.format(pair_name[0], pair_name[1]))
    print('Epoch: {}, Test Loss: {}'.format(epoch, test_loss) )
    model.train()
    train_loss = 0
    for idx, (data, label) in enumerate(tqdm(train_loader)):

        optimizer.zero_grad()
        data = data.to(device)
        label = label.to(device)

        outputs = model(data)
        loss = loss_func(outputs, label)
        loss.backward()
        train_loss += loss.item()
        optimizer.step()

    print('Epoch: {}, Train Loss: {}'.format(epoch, train_loss / len(train_loader)) )


        





