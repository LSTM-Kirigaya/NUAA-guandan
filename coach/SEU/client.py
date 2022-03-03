import json
from ws4py.client.threadedclient import WebSocketClient
from clients.state import State
from coach.SEU.action import Action


class Main(WebSocketClient):

    def __init__(self, url, render):
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
        if "actionList" in message:                                           # 需要做出动作选择时调用动作对象进行解析
            act_index = self.action.rule_parse(message,self.state._myPos,self.state.remain_cards,self.state.history,
                                               self.state.remain_cards_classbynum,self.state.pass_num,
                                               self.state.my_pass_num,self.state.tribute_result)

            # print(act_index)
            self.send(json.dumps({"actIndex": act_index}))