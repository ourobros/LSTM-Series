import torch
import torch.nn as nn 

class Pair_LSTM(nn.Module):

    def __init__(self, embedding_dim, hidden_dim=256, tagset_size=1, dropout=0.2):
        super(Pair_LSTM, self).__init__()
        self.hidden_dim = hidden_dim
        
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers=2, batch_first=True)
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(hidden_dim, tagset_size)


    def forward(self, X):
        lstm_out, _ = self.lstm(X)
        lstm_out = lstm_out[:, -1, :]
        linear_out = self.linear(self.dropout(lstm_out))
        return linear_out


