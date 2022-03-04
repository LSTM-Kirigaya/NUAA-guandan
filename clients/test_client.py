# -*- coding: utf-8 -*-
# @Time       : 2022/3/2
# @Author     : Zhelong Huang
# @File       : test_client.py
# @Description: test the trained model

import sys, os
sys.path.append(os.path.abspath("."))

import json
from ws4py.client.threadedclient import WebSocketClient
from state import State
import argparse
import numpy as np
from util import *
from model import ActionValueNet
from colorama import Back, Style
import torch
import time

arg = argparse.ArgumentParser()
arg.add_argument('-r', '--render', default=False, type=bool)
arg.add_argument('-c', '--client', default="Demo")
arg.add_argument('-d', '--device', default="cpu")
arg.add_argument('--model',        default=None, type=str,  help="path of the model, is None")
arg.add_argument('--lr',           default=1e-3, type=float,help="learning rate of training model")
arg.add_argument('--save_interval',default=1000, type=int,  help="frequency of saving the model")
arg.add_argument('--log_interval', default=100,  type=int,  help="frequency of logging the situation of training")
arg.add_argument('--epsilon',      default=0.1,  type=float,help="epislon-greed strategy probility")
arg.add_argument('--gamma',        default=0.98, type=float,help="decount factor when doing reinforcement learning")
args = vars(arg.parse_args())


MODE          = "Reinforcement Learning"
RENDER        = args["render"]
COACH         = args["client"]
DEVICE        = args["device"]
MODEL         = args["model"]
LEARNING_RATE = args["lr"]
SAVE_INTERVAL = args["save_interval"]
LOG_INTERVAL  = args["log_interval" ]
EPSILON       = args["epsilon"]
GAMMA         = args["gamma"]

check_path(MODEL)
STATE_DICT = torch.load(MODEL)

class ExampleClient(WebSocketClient):
    def __init__(self, url, render=True):
        super().__init__(url)
        self.state = State(render)
        self.action = MLPAction()
        self.render = render
        self.rewards = []
        self.wins = 0

        self.episode = 0            # 从 1 开始计数，每个小局算一个 episode

    def opened(self):
        pass

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def get_reward(self, order):
        myPos = self.state._myPos
        friendPos = (myPos + 2) % 4
        myRank = order.index(myPos)
        friendRank = order.index(friendPos)
        myRank, friendRank = sorted((myRank, friendRank))
        score = (myRank, friendRank)
        if   score == (0, 1):
            reward = 500
        elif score == (0, 2):
            reward = 350
        elif score == (0, 3):
            reward = 100
        elif score == (1, 2):
            reward = - 100
        elif score == (1, 3):
            reward = - 350
        elif score == (2, 3):
            reward = -500
        return reward

    def received_message(self, message):
        message = json.loads(str(message))                                    
        self.state.parse(message)         

        if message["stage"] == "beginning":
            self.episode += 1

        elif message["stage"] == "episodeOver":
            game_order = message["order"]
            reward = self.get_reward(game_order)
            self.rewards.append(reward)
            if reward > 0:
                self.wins += 1

            debugout(self.rewards, "blue")
            debugout("胜率:{}".format(self.wins / len(self.rewards)), "green")

        if "actionList" in message:                                           
            act_index = self.action.parse(message, self.render)
            self.send(json.dumps({"actIndex": act_index}))


class MLPAction(object):
    def __init__(self):
        self.action         = []
        self.act_range      = -1
        self.history_action = [['PASS', 'PASS', 'PASS']]

        # 考虑到我们无法在parse函数的一个生命周期中得到 obs act reward obs_next， 我们需要缓存数据
        # 每次更新前一次的 reward obs_next 和 histroy_next 再更新本次的 obs history 和 act
        
        save_model_class = STATE_DICT.get("model_class", None)
        if save_model_class:
            self.ValueNet = save_model_class().to(DEVICE)
        else:
            self.ValueNet = ActionValueNet().to(DEVICE)
        
        save_state_dict = STATE_DICT.get("model_state_dict", None)
        if save_state_dict:
            self.ValueNet.load_state_dict(save_state_dict)
            print(Back.GREEN, "成功载入模型 : ", MODEL, " 3秒后开始测试", Style.RESET_ALL)
            time.sleep(3)

        self.optimizer = torch.optim.SGD(self.ValueNet.parameters(), lr=LEARNING_RATE)   

    def MapHistoryToLSTM(self):
        ret = torch.stack([encode_card(action).flatten() for action in self.history_action], dim=0)
        ret = ret.unsqueeze(0)
        return ret

    def parse(self, msg, render=True):
        self.action = msg["actionList"]
        self.act_range = msg["indexRange"]          # [0, self.act_range] 的动作都可以选择
        if render:
            # print(self.action)
            print(Back.BLUE, "可选动作范围为: 0至{}".format(self.act_range), Style.RESET_ALL)
        
        state    = StateCatEmbedding(msg)
        history  = self.MapHistoryToLSTM().float().to(DEVICE)

        # 遍历所有的动作，找出最佳的动作，选取Q值最大的动作
        # epislon-greed搜索
        if random.random() > EPSILON:
            q_values = []
            for i in range(self.act_range + 1):
                action   = ActionEmbedding(msg, i)
                state_input = torch.cat((state.flatten(), action.flatten()), dim=0).float().to(DEVICE)
                state_action_input = state_input.unsqueeze(0).float().to(DEVICE)
                q_value : torch.Tensor = self.ValueNet(state_action_input, history).sum()
                q_values.append(q_value.item())
            index = np.argmax(q_values).item()
        else:
            index = random.choice(range(self.act_range + 1))

        self.history_action.append(process_card_list(msg["actionList"][index]))
        return index

if __name__ == '__main__':
    try:
        ws = ExampleClient('ws://127.0.0.1:23456/game/client1', render=RENDER)
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()