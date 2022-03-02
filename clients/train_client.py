# -*- coding: utf-8 -*-
# @Time       : 2022/2/20 16:30
# @Author     : Zhelong Huang
# @File       : train_client.py
# @Description:

import json
from ws4py.client.threadedclient import WebSocketClient
from state import State
from action import Action
from ai_action import MLPAction

import argparse

arg = argparse.ArgumentParser()
arg.add_argument('-r', '--render', default=True)
arg.add_argument('-c', '--client', default="Demo")
args = vars(arg.parse_args())

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


if __name__ == '__main__':
    try:
        ws = ExampleClient('ws://127.0.0.1:23456/game/client1', render=bool(int(args['render'])))
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
