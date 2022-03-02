# -*- coding: utf-8 -*-
# @Time       : 2022/3/2
# @Author     : Zhelong Huang
# @File       : model.py
# @Description: forward model

import torch
from torch import nn
from torch.nn import functional

class CrossUnit(nn.Module):
    def __init__(self, input_dim, inner_dim, out_dim) -> None:
        super().__init__()
        self.fc_1 = nn.Linear(input_dim, inner_dim)
        self.fc_2 = nn.Linear(inner_dim, out_dim)
        self.align = (input_dim == out_dim)
        if not self.align:
            self.fc_3 = nn.Linear(input_dim, out_dim)
    
    def forward(self, x):
        z = self.fc_1(x).relu()
        z = self.fc_2(z)
        if not self.align:
            x = self.fc_3(x)
        return functional.relu(x + z)

    
# 计算当前输入message中某一个action的值
class ActionValueNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(60, 256, batch_first=True)
        self.total_cross = nn.Sequential(
            CrossUnit(493 + 256, 512, 512),
            CrossUnit(512      , 512, 512),
            CrossUnit(512      , 512, 512),
            CrossUnit(512      , 512, 512),
            CrossUnit(512      , 512, 1  )
        )
    
    def forward(self, state, history):
        # state : [B, 492]
        # history : [B, T, 60]
        out, (h_n, _) = self.lstm(history)
        # out : [1, T, 256]
        # h_n : [1, 1, 256]
        state = torch.cat((out[:, -1, :], state), dim=1)
        value = self.total_cross(state)
        return value