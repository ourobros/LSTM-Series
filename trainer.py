import numpy as np
import pandas as pd
import ta
import sys
from datetime import datetime
from tqdm import tqdm
import torch

from model import Pair_LSTM
from utils import *
from dataset_train import Pair_Dataset_Train
from dataset_test import Pair_Dataset_Test

import yaml


class Trainer():
    def __init__(self, config):
        self.data_path = config['data']['data_path']
        self.pair_name = [config['data']['future1_name'], config['data']['future2_name']]
        self.params = config['preprocess_data']
        self.epochs = config['train']['epochs']
        self.ts_length = config['train']['ts_length']
        self.device = config['train']['device']
        self.train_data_precent = config['train']['train_data_precent']
        self.train_dataset = self.create_train_dataset()
        self.test_dataset = self.create_test_dataset()

        self.train_loader = torch.utils.data.DataLoader(self.train_dataset, batch_size=32, shuffle=True)
        self.test_loader = torch.utils.data.DataLoader(self.test_dataset, batch_size=1, shuffle=False)

        self.model = Pair_LSTM(self.train_dataset[0][0].shape[1])
        self.model = self.model.to(self.device)
        self.loss_func = torch.nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-3)
        
    
    def get_start_end(self, is_train=True):
        tmp_df = pd.read_csv(os.path.join(self.data_path, self.pair_name[0] + '_5m.csv'))
        length_tmp_df = tmp_df.shape[0]
        if is_train:
            start = str(tmp_df.datetime[0])
            end = str(tmp_df.datetime[int(length_tmp_df * self.train_data_precent)])
        else:
            start = str(tmp_df.datetime[int(length_tmp_df * self.train_data_precent) + 1])
            end = str(tmp_df.datetime[length_tmp_df - 1])
        return start, end

    def create_train_dataset(self):
        train_start, train_end = self.get_start_end(is_train=True)
        train_pair_infos = get_datas(data_path=self.data_path, pair_name=self.pair_name, 
                                     start_time=train_start, end_time=train_end)
        train_pair_data = get_pair_datas(train_pair_infos, self.pair_name)
        train_pair_data, coffis = get_indicators(train_pair_data, self.params, return_beginINDEX=True)
        self.params.update(coffis)
        self.train_dataset = Pair_Dataset_Train(train_pair_data, ts_length=self.ts_length)
        return self.train_dataset

    def create_test_dataset(self):
        assert self.train_dataset is not None, 'Please create traindataset first'
        test_start, test_end = self.get_start_end(is_train=False)
        test_pair_infos = get_datas(data_path=self.data_path, pair_name=self.pair_name, 
                                    start_time=test_start, end_time=test_end)
        test_pair_data = get_pair_datas(test_pair_infos, self.pair_name)
        self.test_dataset = Pair_Dataset_Test(test_pair_data, self.params, 
                                              self.ts_length, self.train_dataset.minmax_dict)
        return self.test_dataset

    def train(self):
        print('------BEGIN TRAINING------')
        best_test_loss = 10000
        for epoch in range(self.epochs):
            test_loss = test(self.model, self.test_loader)
            if test_loss < best_test_loss:
                best_test_loss = test_loss
                dicts = {'pair_names': self.pair_name, 
                         'params': self.params, 
                         'model': self.model.state_dict(), 
                         'minmax_dict': self.train_dataset.minmax_dict, 
                         'ts_length': self.ts_length}
                torch.save(dicts, '{}-{}-lstm.pth'.format(self.pair_name[0], self.pair_name[1]))
            print('Epoch: {}, Test Loss: {}'.format(epoch, test_loss))
            self.model.train()
            train_loss = 0
            for idx, (data, label) in enumerate(tqdm(self.train_loader)):
                self.optimizer.zero_grad()
                data = data.to(self.device)
                label = label.to(self.device)
                outputs = self.model(data)
                loss = self.loss_func(outputs, label)
                loss.backward()
                train_loss += loss.item()
                self.optimizer.step()
            print('Epoch: {}, Train Loss: {}'.format(epoch, train_loss / len(self.train_loader)))

    def get_checkpoint_name(self):
        return '{}-{}-lstm.pth'.format(self.pair_name[0], self.pair_name[1])

                            
