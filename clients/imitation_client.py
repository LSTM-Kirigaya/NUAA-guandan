# -*- coding: utf-8 -*-
# @Time       : 2022/2/23
# @Author     : Zhelong Huang
# @File       : imitation_client.py
# @Description: imitation learning module

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
args = vars(arg.parse_args())

MODE          = "Imitation Learning"
RENDER        = args["render"]
COACH         = args["client"]
DEVICE        = args["device"]
MODEL         = args["model"]
LEARNING_RATE = args["lr"]
SAVE_INTERVAL = args["save_interval"]
LOG_INTERVAL  = args["log_interval" ]


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
    def __init__(self, url, render=False):
        super().__init__(url)
        self.state = State(render)
        self.action = MLPAction()
        self.render = render

    def opened(self):
        pass

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, message):
        message = json.loads(str(message))
        self.state.parse(message)

        if "actionList" in message:           
            act_index = self.action.parse(message, self.render)
            self.send(json.dumps({"actIndex": act_index}))


class MLPAction(object):
    def __init__(self):
        self.action         = []
        self.act_range      = -1
        self.history_action = [['PASS', 'PASS', 'PASS']]
        self.count  = 0
        
        save_model_class = STATE_DICT.get("model_class", None)
        if save_model_class:
            self.ValueNet = save_model_class().to(DEVICE)
        else:
            self.ValueNet = ActionValueNet().to(DEVICE)
        
        save_state_dict = STATE_DICT.get("model_state_dict", None)
        if save_state_dict:
            self.ValueNet.load_state_dict(save_state_dict)

        self.optimizer = torch.optim.SGD(self.ValueNet.parameters(), lr=LEARNING_RATE)   

        # TODO : 未来这个名字应该就只叫做self.action
        self.eggpan_action = Action(render=RENDER)
    
    def MapHistoryToLSTM(self):
        ret = torch.stack([encode_card(action).flatten() for action in self.history_action], dim=0)
        ret = ret.unsqueeze(0)
        return ret
    
    def update(self, loss : torch.Tensor):
        # loss : 需要被最小化的值
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def parse(self, msg, render=True):
        self.action = msg["actionList"]
        self.act_range = msg["indexRange"]
        if render:
            # print(self.action)
            print(Back.BLUE, "可选动作范围为: 0至{}".format(self.act_range), Style.RESET_ALL)
        
        index = self.eggpan_action.parse_AI(msg, msg.get("myPos", 0))
        index = np.clip(index, 0, self.act_range).tolist()

        state       = StateCatEmbedding(msg)
        demo_action = ActionEmbedding(msg, index)
        history     = self.MapHistoryToLSTM().float().to(DEVICE)

        state_input = torch.cat((state.flatten(), demo_action.flatten()), dim=0).float().to(DEVICE)
        state_input = state_input.unsqueeze(0).float().to(DEVICE)

        # @debug
        # print(state_input.shape)
        # print(RENDER)
        # print(type(RENDER))
        # time.sleep(3)

        # state_input shape torch.Size([1, 493])
        value : torch.Tensor = self.ValueNet(state_input, history).sum()
        # 最大化选中的值，就是最小化负值
        loss = - value
        self.update(loss)

        cur_val = value.detach().cpu().numpy().tolist()

        if self.count % SAVE_INTERVAL == 0:
            torch.save({
                "coach" : COACH,
                "mode"  : MODE,
                "model_state_dict" : self.ValueNet.state_dict(),
                "model_class"  : ActionValueNet
            }, CHECK_PATH + "/{}_value_{}.pth".format(now_str(), round(cur_val, 3)))
        
        if self.count % LOG_INTERVAL == 0:
            with open(CHECK_PATH + "/value.log", "a", encoding="utf-8") as fp:
                fp.write("[count={}] value = {}\n".format(self.count, - loss.item()))

        self.history_action.append(process_card_list(msg["actionList"][index]))
        self.count += 1
        return index

if __name__ == '__main__':
    try:
        ws = ExampleClient('ws://127.0.0.1:23456/game/client1', render=bool(RENDER))
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()