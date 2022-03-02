import sys, os
from pprint import pprint
sys.path.append(os.path.abspath("."))

import numpy as np
from util import *
from model import ActionValueNet
from colorama import Back, Style
import torch



class MLPAction(object):
    ValueNet = ActionValueNet()
    def __init__(self):
        self.action         = []
        self.act_range      = -1
        self.history_action = [['PASS', 'PASS', 'PASS']]
    
    def MapHistoryToLSTM(self):
        ret = torch.stack([encode_card(action).flatten() for action in self.history_action], dim=0)
        ret = ret.unsqueeze(0)
        return ret

    def parse(self, msg, render=True):
        self.action = msg["actionList"]
        self.act_range = msg["indexRange"]
        if render:
            # print(self.action)
            print(Back.BLUE, "可选动作范围为: 0至{}".format(self.act_range), Style.RESET_ALL)
        
        index = int(input("请输入 > "))
        index = np.clip(index, 0, self.act_range).tolist()

        state       = StateCatEmbedding(msg)
        demo_action = ActionEmbedding(msg, index)
        history     = self.MapHistoryToLSTM()

        state_input = torch.cat((state.flatten(), demo_action.flatten()), dim=0)
        state_input = state_input.unsqueeze(0)

        self.ValueNet(state_input, history)

        self.history_action.append(process_card_list(msg["actionList"][index]))
        return index