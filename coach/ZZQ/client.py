# -*- coding: utf-8 -*-
# @Time       : 2020/10/1 16:30
# @Author     : Duofeng Wu
# @File       : client.py
# @Description:
# 我们AI加持的玩家1


import json
pos = 0
from ws4py.client.threadedclient import WebSocketClient
from clients.state import State
from coach.ZZQ.action import Action


class Main(WebSocketClient):

    def __init__(self, url):
        super().__init__(url)
        self.state = State()
        self.action = Action()

    def opened(self):
        pass

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, message):
        message = json.loads(str(message))                                    # 先序列化收到的消息，转为Python中的字典
        self.state.parse(message)
        if 'myPos' in message:
            global pos
            pos = message['myPos']
        # 调用状态对象来解析状态
        if "actionList" in message:    # 需要做出动作选择时调用动作对象进行解析
            #由AI进行选择，座位号确定为0
            act_index = self.action.parse_AI(message, pos) #pos
            self.send(json.dumps({"actIndex": act_index}))
