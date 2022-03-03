import json
from ws4py.client.threadedclient import WebSocketClient
from clients.state import State
from coach.EggPan.action import Action
import os

pos = 0

class Main(WebSocketClient):
    def __init__(self, url, render=True):
        super().__init__(url)
        self.state = State(render)
        self.action = Action(render)

    def opened(self):
        pass

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, message):
        message = json.loads(str(message))                                    # 先序列化收到的消息，转为Python中的字典
        self.state.parse(message)                                             # 调用状态对象来解析状态

        if 'myPos' in message:            
            global pos             
            pos = message['myPos']

        if "actionList" in message:    # 需要做出动作选择时调用动作对象进行解析
            #由AI进行选择，座位号随时读取
            act_index = self.action.parse_AI(message, pos)
            self.send(json.dumps({"actIndex": act_index}))