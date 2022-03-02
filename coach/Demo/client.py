import json
from ws4py.client.threadedclient import WebSocketClient
from clients.state import State
from coach.Demo.action import Action
from colorama import Back, Style

class Main(WebSocketClient):

    def __init__(self, url, render=True):
        super().__init__(url)
        self.state = State(render)
        self.action = Action(render)
        self.render = render

    def opened(self):
        pass

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, message):
        message = json.loads(str(message))                                    # 先序列化收到的消息，转为Python中的字典
        self.state.parse(message)                                             # 调用状态对象来解析状态
        if message["stage"] == "gameOver":
            self.close()
        if "actionList" in message:                                           # 需要做出动作选择时调用动作对象进行解析
            act_index = self.action.parse(message)
            self.send(json.dumps({"actIndex": act_index}))