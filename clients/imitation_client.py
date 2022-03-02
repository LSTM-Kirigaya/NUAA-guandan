# -*- coding: utf-8 -*-
# @Time       : 2022/2/20 16:30
# @Author     : Zhelong Huang
# @File       : imitation_client.py
# @Description: imitation module

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

from coach.EggPan.action import Action

arg = argparse.ArgumentParser()
arg.add_argument('-r', '--render', default=True)
arg.add_argument('-c', '--client', default="Demo")
arg.add_argument('-d', '--device', default="cpu")
arg.add_argument('--model',        default="",              help="path of the model, is None")
arg.add_argument('--lr',           default=1e-3, type=float,help="learning rate of training model")
arg.add_argument('--save_interval',default=1000, type=int,  help="frequency of saving the model")
arg.add_argument('--log_interval', default=100,  type=int,  help="frequency of logging the situation of training")
args = vars(arg.parse_args())

CHECK_PATH = "model/checkpoints_{}".format(now_str())
if not os.path.exists(CHECK_PATH):
    os.makedirs(CHECK_PATH)

LEARNING_RATE = args["lr"]
SAVE_INTERVAL = args["save_interval"]
LOG_INTERVAL  = args["log_interval" ]
DEVICE        = args["device"]
COACH         = args["client"]

with open(CHECK_PATH + "/value.log", "a", encoding="utf-8") as fp:
    fp.write("* LEARNING_RATE : {}\n".format(LEARNING_RATE))
    fp.write("* SAVE_INTERVAL : {}\n".format(SAVE_INTERVAL))
    fp.write("* LOG_INTERVAL  : {}\n".format(LEARNING_RATE))
    fp.write("* DEVICE : {}\n".format(DEVICE))

class ExampleClient(WebSocketClient):
    def __init__(self, url, render=True):
        super().__init__(url)
        self.state = State(render)
        self.action = MLPAction()
        self.render = render

    def opened(self):
        pass

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, message):
        message = json.loads(str(message))                                    # 先序列化收到的消息，转为Python中的字典
        self.state.parse(message)                                             # 调用状态对象来解析状态
        if "actionList" in message:                                           # 需要做出动作选择时调用动作对象进行解析
            act_index = self.action.parse(message, self.render)
            self.send(json.dumps({"actIndex": act_index}))


class MLPAction(object):
    ValueNet = ActionValueNet().to(DEVICE)
    eggpan_action = Action(render=False)
    def __init__(self):
        self.action         = []
        self.act_range      = -1
        self.history_action = [['PASS', 'PASS', 'PASS']]
        self.count  = 0
        self.optimizer = torch.optim.SGD(self.ValueNet.parameters(), lr=LEARNING_RATE)    
    
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

        value : torch.Tensor = self.ValueNet(state_input, history).sum()
        # 最大化选中的值，就是最小化负值
        loss = - value
        self.update(loss)

        cur_val = (- value).detach().cpu().numpy().tolist()

        if self.count % SAVE_INTERVAL == 0:
            torch.save({
                "coach" : COACH,
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
        ws = ExampleClient('ws://127.0.0.1:23456/game/client1', render=bool(int(args['render'])))
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()