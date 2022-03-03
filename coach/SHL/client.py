# -*- coding: utf-8 -*-
# @Time       : 2020/10/1 16:30
# @Author     : HaiLong Sun
# @File       : client_pjh3.py
# @Description:


import json
from ws4py.client.threadedclient import WebSocketClient
from clients.state import State
from coach.SHL.action import Action_shl


class Main(WebSocketClient):

    def __init__(self, url, render=True):
        super().__init__(url)
        self.state = State(render)         #动作执行的状态
        self.action = Action_shl(render)   #动作的算法
        self.rounds = 0              #回合数
        self.my_pos = None           #当前的位置
        self.cards_num = dict()
        self.curRank = None          #当前等级
    def opened(self):
        pass

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, message):
        message = json.loads(str(message))                       # 先序列化收到的消息，转为Python中的字典
        self.state.parse(message)                                # 调用状态对象来解析状态

        if message["stage"] == "beginning":
            self.my_pos = message['myPos']
            self.action.initcards(message)

        if message["type"] == "act":
            self.curRank = message['curRank']

        if message["stage"] == "episodeOver":  # 小局结束，回合数清零
            self.rounds = 0

        if "actionList" in message:  # 需要做出动作选择时调用动作对象进行解析
            self.rounds += 1  # 回合数加1
            # print("handcards:", message["handCards"])
        # 解析当前state（服务器的message、agent剩余卡牌数量、目前的回合数、位置）
            if message["stage"] == "tribute":
                act_index = 0
            else:
                self.action.initcards(message)
                act_index = self.action.parse(msg=message,
                                              rounds=self.rounds,
                                              my_pos=self.my_pos)

            self.send(json.dumps({"actIndex": act_index}))