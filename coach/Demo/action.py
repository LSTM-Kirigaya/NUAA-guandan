from random import randint

class Action(object):
    def __init__(self, render=True) -> None:
        self.render = render
    
    def parse(self, msg):
        self.action = msg["actionList"]
        self.act_range = msg["indexRange"]
        if self.render:
            print(self.action)
            print("可选动作范围为:0至{}".format(self.act_range))
        return randint(0, self.act_range)