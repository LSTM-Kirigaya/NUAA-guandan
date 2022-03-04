# -*- coding: utf-8 -*-
# @Time       : 2022/3/2
# @Author     : Zhelong Huang
# @File       : reinforcement_client.py
# @Description: reinforcement learning module

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

from coach.EggPan.action import Action

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

CHECK_PATH = "model/checkpoints_{}".format(now_str())
if not os.path.exists(CHECK_PATH):
    os.makedirs(CHECK_PATH)

if MODEL is None or MODEL != "None":
    check_path(MODEL)
    STATE_DICT = torch.load(MODEL)
else:
    STATE_DICT = {}


with open(CHECK_PATH + "/value.log", "a", encoding="utf-8") as fp:
    fp.write("* LEARNING_RATE : {}\n".format(LEARNING_RATE))
    fp.write("* SAVE_INTERVAL : {}\n".format(SAVE_INTERVAL))
    fp.write("* LOG_INTERVAL  : {}\n".format(LEARNING_RATE))
    fp.write("* DEVICE : {}\n".format(DEVICE))
    fp.write("* MODE : {}\n".format(MODE))
  

class ExampleClient(WebSocketClient):
    def __init__(self, url, render=True):
        super().__init__(url)
        self.state = State(render)
        self.action = MLPAction()
        self.render = render

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
            self.action.clear_temp()
            self.episode += 1

        elif message["stage"] == "episodeOver":
            game_order = message["order"]
            reward = self.get_reward(game_order)
            history = self.action.MapHistoryToLSTM().to(DEVICE)
            self.action.update_post(reward=reward, obs_next=None, history_next=history, done=True, actionListNext=None)
            self.action.send_buffer()

            # 进行更新
            losses, rewards = self.action.replay_memory.learn_from(
                gamma=GAMMA, 
                optimizer=self.action.optimizer,
                ValueNet=self.action.ValueNet,
                device=DEVICE
            )
            
            if self.episode % SAVE_INTERVAL == 0:
                torch.save({
                    "coach" : COACH,
                    "MODE"  : MODE,
                    "model_state_dict" : self.action.ValueNet.state_dict(),
                    "model_class"  : ActionValueNet
                }, CHECK_PATH + "/{}_reward_{}.pth".format(now_str(), round(sum(rewards), 3)))
        
            if self.episode % LOG_INTERVAL == 0:
                with open(CHECK_PATH + "/value.log", "a", encoding="utf-8") as fp:
                    fp.write("[epsiode={}] avgloss = {} reward = {}\n".format(self.episode, np.mean(losses), sum(rewards)))
             

        if "actionList" in message:                                           
            act_index = self.action.parse(message, self.render)
            self.send(json.dumps({"actIndex": act_index}))


class MLPAction(object):
    def __init__(self):
        self.action         = []
        self.act_range      = -1
        self.history_action = [['PASS', 'PASS', 'PASS']]

        self.replay_memory = MemoryBuffer()

        # 考虑到我们无法在parse函数的一个生命周期中得到 obs act reward obs_next， 我们需要缓存数据
        # 每次更新前一次的 reward obs_next 和 histroy_next 再更新本次的 obs history 和 act
        self.temp_store = {
            "obs"            : None,
            "history"        : None,
            "act"            : None,
            "reward"         : None,
            "obs_next"       : None,
            "actionListNext" : None,
            "history_next"   : None,
            "done"           : False,
        }
        
        save_model_class = STATE_DICT.get("model_class", None)
        if save_model_class:
            self.ValueNet = save_model_class().to(DEVICE)
        else:
            self.ValueNet = ActionValueNet().to(DEVICE)
        
        save_state_dict = STATE_DICT.get("model_state_dict", None)
        if save_state_dict:
            self.ValueNet.load_state_dict(save_state_dict)
            print(Back.GREEN, "成功载入模型 : ", MODEL, " 3秒后开始训练", Style.RESET_ALL)
            time.sleep(3)

        self.optimizer = torch.optim.SGD(self.ValueNet.parameters(), lr=LEARNING_RATE)   

    def MapHistoryToLSTM(self):
        ret = torch.stack([encode_card(action).flatten() for action in self.history_action], dim=0)
        ret = ret.unsqueeze(0)
        return ret

    def clear_temp(self):
        for k in self.temp_store:
            self.temp_store[k] = None
        self.temp_store["done"] = False
    
    def update_pre(self, obs, history, act):
        self.temp_store["obs"] = obs
        self.temp_store["history"] = history
        self.temp_store["act"] = act


    def update_post(self, reward, obs_next, actionListNext, history_next, done):
        self.temp_store["reward"] = reward
        self.temp_store["obs_next"] = obs_next
        self.temp_store["actionListNext"] = actionListNext
        self.temp_store["history_next"] = history_next
        self.temp_store["done"] = done

   # 将缓存发送给 回放池
    def send_buffer(self):
        self.replay_memory.append((
            self.temp_store["obs"],
            self.temp_store["history"],
            self.temp_store["act"],                 # 可以直接扔进encode_card
            self.temp_store["reward"],
            self.temp_store["obs_next"],
            self.temp_store["actionListNext"],      # 原本的actionList
            self.temp_store["history_next"],
            self.temp_store["done"]
        ))

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
        
        act = process_card_list(self.action[index])
        self.update_post(reward=0, obs_next=state, actionListNext=self.action, history_next=history, done=False)
        if self.temp_store["obs"] is not None and self.temp_store["history"] is not None:
            self.send_buffer()

        self.update_pre(obs=state, history=history, act=act)
        # 输入： state, action, history
        # 整合策略： state + history -> state  action -> action

        self.history_action.append(process_card_list(msg["actionList"][index]))

        return index

if __name__ == '__main__':
    try:
        ws = ExampleClient('ws://127.0.0.1:23456/game/client1', render=RENDER)
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()