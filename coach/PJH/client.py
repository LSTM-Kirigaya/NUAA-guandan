import json
from ws4py.client.threadedclient import WebSocketClient
from clients.state import State
from coach.PJH.AIAction_back import AIAction

episode_result_list = []    # 记录每个小局结束时的记录
first_end_agent_count = {
    0 : 0, 1 : 0, 2 : 0, 3 : 0
}      # 统计每个agent出完牌的次数
train = False


class Main(WebSocketClient):
    def __init__(self, url, render=True):
        
        super().__init__(url)
        self.state = State(render)            # 获取agent所处环境对象
        self.action = AIAction(render)        # 获取agent动作决策对象
        self.restCards = None           # 剩余的卡牌,agent所剩余的卡牌，我们在开始的时候进行初始化
        self.episode_rounds = 0         # 当前小局玩的回合数，
        self.agent_pos = None           # agent所处的位置，这个是座位的位置,我们在一大局开始的时候进行更新
        self.allRestCards = None        # 这个变量用来记录当前另外三家所有的牌，一小局开始的时候我们插入完整的牌，并减去手牌

    def opened(self):
        pass

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    # 两个列表做减法
    def listMinus(self, list1, list2):
        for item in list2:
            if item in list1:
                list1.remove(item)
        return list1

    # 输入动作三元组来更新剩余卡片，这个函数的作用是进行更新，也就是在自己的牌发生变化时，对手牌的列表进行更新
    def updateRestCards(self, act_trip):
        # 牌型、点数、卡牌
        card_type, card_num, cards = act_trip    #对传入的三元组进行内容的提取
        if card_type == "PASS":             # 过
            pass
        elif card_type == "tribute":        # 进贡
            self.listMinus(self.restCards, cards)
        elif card_type == "back":           # 还贡
            self.restCards += cards
        else:                                            # 其余情况:正常出牌
            self.listMinus(self.restCards, cards)

    #更新所有未知的牌，只有在其他三家进行出牌的时候进行更新,我们会只传入act阶段其他三家的动作

    def updateAllRestCards(self,act_trip):
        card_type, card_num, cards = act_trip

        if card_type == "PASS":     #如果其他三家进行了PASS操作，那么对牌堆无影响
            pass
        
        else:
            self.listMinus(self.allRestCards, cards)             #如果是act阶段的，那么对其进行记录

    def received_message(self, message):
        
        message = json.loads(str(message))                                    # 先序列化收到的消息，转为Python中的字典

        self.state.parse(message)                                                     # 调用状态对象来解析状态

        # 如果是开头，将我们有的卡牌存下来，并获取座位号
        # message type : dict
        if message["stage"] == "beginning":
            self.restCards = message["handCards"]
            self.agent_pos = message["myPos"]


        # 小局结束，回合数清零，并记录一下结果
        if message["stage"] == "episodeOver":
            global episode_result_list, first_end_agent_count
            self.episode_rounds == 0
            episode_result_list.append(message["order"])     # 保留第一个出完牌的agent
            first_end_agent_count[message["order"][0]] += 1     # 计数器+1


        # 目前存在可选动作列表，代表目前可以打牌
        if "actionList" in message:
            # 回合数+1
            self.episode_rounds += 1
            
            print("剩余卡牌:", self.restCards)

            # 解析当前state（服务器的message、agent剩余卡牌数量、目前的回合数、位置）
            index = self.action.parse(msg=message,
                                          restCards=self.restCards,
                                          episode_rounds=self.episode_rounds,
                                          agent_pos=self.agent_pos)

            # 得到代表打牌动作的三元组
            act_index = int (index) 
            act_trip = message["actionList"][act_index]
            # 更新手牌
            self.updateRestCards(act_trip)
            self.send(json.dumps({"actIndex": act_index}))