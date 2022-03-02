# -*- coding: utf-8 -*-
# @Time       : 2020/10/1 21:32
# @Author     : Duofeng Wu
# @File       : action.py
# @Description: 动作类

from random import randint
from coach.QAI.mysolve import solve


class Action(object):

    def __init__(self, render):
        self.action = []
        self.act_range = -1
        self.render = render
        self.pos = -1

    def parse(self, msg):
        self.action = msg["actionList"]
        self.act_range = msg["indexRange"]
        if self.render:
            print(self.action)
            print("可选动作范围为:0至{}".format(self.act_range))
        index = randint(0, self.act_range)
        if self.pos != -1:
            index = solve(msg, self.pos)
        return index
