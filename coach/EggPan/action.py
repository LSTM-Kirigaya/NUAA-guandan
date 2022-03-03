from random import randint
from coach.EggPan.message_Reyn_CUR2 import check_message
import os

class Action(object):
    def __init__(self, render=True):
        self.action = []
        self.act_range = -1
        self.AI_choice = -1
        self.render = render

    #该为完全随机数的行动
    def parse(self, msg):
        self.action = msg["actionList"]
        self.act_range = msg["indexRange"]
        if self.render:
            print(self.action)
            print("可选动作范围为:0至{}".format(self.act_range))
        return randint(0, self.act_range)

    #该为有AI加持的确定行动
    def parse_AI(self, msg, pos):
        self.action = msg["actionList"]
        self.act_range = msg["indexRange"]
        if self.render:
            print(self.action)
        

        #运行AI来确定需要出的牌
        self.AI_choice = check_message(msg, pos)
        #由于没有考虑进贡，故而随机，否则bug
        if self.AI_choice == None:
            return randint(0, self.act_range)
        if self.render:
            print("AI选择的出牌编号为:{}".format(self.AI_choice))
        return self.AI_choice