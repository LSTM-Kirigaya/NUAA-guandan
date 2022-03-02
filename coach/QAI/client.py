# -*- coding: utf-8 -*-
# @Time       : 2020/10/1 16:30
# @Author     : Duofeng Wu
# @File       : client.py
# @Description:


import json
from ws4py.client.threadedclient import WebSocketClient
from clients.state import State
from coach.QAI.action import Action


class Main(WebSocketClient):

    def __init__(self, url, render=True):
        super().__init__(url)
        self.state = State(render)
        self.action = Action(render)
        self.pos = -1

    def opened(self):
        pass

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, message):
        message = json.loads(str(message))                                    # 先序列化收到的消息，转为Python中的字典
        self.state.parse(message)
        if message["stage"] == "beginning":
            if message["myPos"] == 1:
                self.pos = 3
            elif message["myPos"] == 2:  # 调用状态对象来解析状态
                self.pos = 0
            elif message["myPos"] == 3:
                self.pos = 1
            elif message["myPos"] == 0:
                self.pos = 2  
            self.action.pos = self.pos                                                  # 调用状态对象来解析状态
        if "actionList" in message:                                           # 需要做出动作选择时调用动作对象进行解析
            act_index = self.action.parse(message)
            # act_index = self.action.parse(message, -1)
            self.send(json.dumps({"actIndex": act_index}))
