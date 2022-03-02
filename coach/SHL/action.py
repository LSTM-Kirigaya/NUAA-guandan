# -*- coding: utf-8 -*-
# @Time       : 2020/10/16 16:35
# @Author     : HaiLong Sun
# @File       : action_shl.py
# @Description: 动作类

from random import randint

# 中英文对照表
ENG2CH = {
    "Single": "单张",
    "Pair": "对子",
    "Trips": "三张",
    "ThreePair": "三连对",
    "ThreeWithTwo": "三带二",
    "TwoTrips": "钢板",
    "Straight": "顺子",
    "StraightFlush": "同花顺",
    "Bomb": "炸弹",
    "PASS": "过"
}

# 牌到点数的映射
card2num = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,"7": 7,"8": 8,
    "9": 9, "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14, "B": 15,"R": 16,
}
number_list = ['Single', 'Pair', 'Trips']
ONLY_SAME_TYPE = 0
ONLY_BOMB = 1
SAME_TYPE_AND_BOMB = 2
cards_order = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A', 'B', 'R']

class Action_shl(object):

    def __init__(self, render=True):
        self.actionList = []                    # 当前的动作列表
        self.act_range = -1                     # 可执行动作范围
        self.handCards = []                     # agent剩余手牌
        self.ideal_round = 5                    # 理想的回合数，在该值之前不出炸弹
        self.rounds = 0                         # 回合数
        self.agent_pos = None                   # 位置
        self.opponent1_rest_cards = []          # 对手1剩余的牌数
        self.opponent2_rest_cards = []          # 对手2剩余的牌数
        self.cards_type_num_dict = dict()       # 花色牌的剩余牌数（最多两张）
        self.ban_cards_list = []                # 不能出的牌的列表
        # self.cards_number_count_dict = dict() # 各种点数的剩余牌数（字典类型，最多八张）
        self.hongTaoRank = 0                    # 红心配
        self.actionIndexList = []               # 过滤后的动作列表的下标
        self.actionListFiltered = []            # 过滤后的动作
        self.cards_number_count_list = []       # 各种点数的剩余牌数，并且是降序排序（列表类型，最多八张）
        self.cards_number_count_dict = {'2': 0, '3': 0, '4': 0, '5': 0, '6': 0,
                                        '7': 0, '8': 0, '9': 0, 'T': 0, 'J': 0,
                                        'Q': 0, 'K': 0, 'A': 0, 'B': 0, 'R': 0}
        self.render = render
    # 记录牌数 + 理牌
    def initcards(self, msg):
        self.handCards = msg['handCards']
        # self.hongTaoRank = 'H' + curRank
        self.count_cards_init()
        self.manage_cards()
        if self.render:
            print(self.cards_number_count_dict)

    # 开局记录各种花色牌的牌数
    def count_cards_init(self):
        self.cards_type_num_dict = {}
        for i in self.handCards:
            if i in self.cards_type_num_dict.keys():
                self.cards_type_num_dict[i] += 1
            else:
                self.cards_type_num_dict[i] = 1

    # 理牌 （用花色牌的字典生成各种点数牌的牌数字典）
    def manage_cards(self):
        # hongXinPeiNumber = self.cards_type_num_dict[self.hongTaoRank]
        self.cards_number_count_dict = {'2': 0, '3': 0, '4': 0, '5': 0, '6': 0,
                                        '7': 0, '8': 0, '9': 0, 'T': 0, 'J': 0,
                                        'Q': 0, 'K': 0, 'A': 0, 'B': 0, 'R': 0}
        for i in self.handCards:
            if i[1] in self.cards_number_count_dict.keys():
                self.cards_number_count_dict[i[1]] += 1
            else:
                self.cards_number_count_dict[i[1]] = 1

        # 根据牌数进行升序排序
        self.cards_number_count_list = sorted(self.cards_number_count_dict.items(), key=lambda x: x[1], reverse=False)

    # 过滤动作列表 将能构成炸弹的牌保留下来，不能拆掉
    def filterActionList(self):
        self.ban_cards_list = []
        pick_index = []  # 动作列表里能出的动作的下标
        count = 0
        for number, shuliang in self.cards_number_count_dict.items():
            if shuliang >= 4:  # 如果牌数大于4 则放入ban_cards_list
                self.ban_cards_list.append(number)

        for action in self.actionList:
            flag = True
            if action[2] == 'PASS':     # 如果动作为pass，则放入pick_index里面
                self.actionListFiltered.append(action)
                pick_index.append(count)
            else:
                for j in action[2]:
                    if j[1] in self.ban_cards_list:  # 如果牌在ban_cards_list里面，则不加入pick_index
                        flag = False
                        break
                if flag:        # 如果牌不在ban_cards_list里面，则加入pick_index
                    self.actionListFiltered.append(action)
                    pick_index.append(count)
            count += 1
        return pick_index

    def algorithm(self, msg):
        # 还贡阶段 todo 还要考虑是还给队友，还是对手
        if msg["stage"] == "back":
            for i in range(len(msg['actionList'])):
                number_str = msg['actionList'][i][2][0][1]
                if self.cards_number_count_dict[number_str] == 1:  # 将手牌中单牌里最小的牌还贡
                    return i

        # 自己的牌最大，轮到自己出牌
        if msg["greaterPos"] == -1:
            return self.greaterpos_is_myself(msg)

        # 没有牌可以出
        if len(self.actionList) == 1:
            return 0

        # 判断动作列表里的牌类型（只有炸弹，只有相同类型的牌，两者均有）
        flag = self.type_flag(self.actionList)
        # 出牌阶段
        if msg["greaterPos"] == (self.agent_pos + 2) % 4:           # 队友的牌为最大
            return self.greaterpos_is_teammate(msg, flag)
        else:
            return self.greaterpos_is_opponent(msg, flag)           # 对手的牌最大

    def order_of_play(self, msg):
        curRank = msg['curRank']

        # 我们先出钢板
        for i in self.actionIndexList:
            if self.actionList[i][0] == 'TwoTrips':
                if self.actionList[i][1] in ['Q', 'K', 'A', curRank]:
                    pass
                else:
                    for j in self.actionList[i][2]:
                        self.cards_number_count_dict[j[1]] -= 1
                    return i
        # 如果没有钢板，就出三连对
        for i in self.actionIndexList:
            if self.actionList[i][0] == 'ThreePair':
                if self.actionList[i][1] in ['Q']:
                    pass
                else:
                    for j in self.actionList[i][2]:
                        self.cards_number_count_dict[j[1]] -= 1
                    return i
        # 如果有王，则出单只
        if self.cards_number_count_dict['B'] > 0 or self.cards_number_count_dict['R'] > 0:
            for i in self.actionIndexList:
                if self.actionList[i][0] == 'Single' and self.cards_number_count_dict[self.actionList[i][1]] == 1:
                    if self.actionList[i][1] in [curRank, 'B', 'R']:
                        if len(msg['handCards']) <= 6:  # 当手牌较小时，有可能有炸弹和王
                            for j in self.actionList[i][2]:
                                self.cards_number_count_dict[j[1]] -= 1
                            return i
                        else:
                            pass
                    else:
                        for j in self.actionList[i][2]:
                            self.cards_number_count_dict[j[1]] -= 1
                        return i
        # 如果没有三连对，就出三带二
        for i in self.actionIndexList:
            if self.actionList[i][0] == 'ThreeWithTwo':
                if self.cards_number_count_dict[self.actionList[i][1]] == 3 and \
                     self.cards_number_count_dict[self.actionList[i][2][3][1]] == 2 and \
                        self.actionList[i][2][3][1] not in ['K', 'A', curRank, 'B', 'R']:  # 带的对子不能是这些
                    for j in self.actionList[i][2]:
                        self.cards_number_count_dict[j[1]] -= 1
                    return i
        for i in self.actionIndexList:
            if self.actionList[i][0] == 'Trips':
                for j in self.actionList[i][2]:
                    self.cards_number_count_dict[j[1]] -= 1
                return i
        # 先出单张，将单张全部出完后再出对子，然后出三不带
        for i in self.actionIndexList:
            if self.cards_number_count_list[0][0] == self.actionList[i][1] and \
                    self.cards_number_count_list[0][1] == number_list.index(self.actionList[i][0]) + 1:
                for j in self.actionList[i][2]:
                    self.cards_number_count_dict[j[1]] -= 1
                return i
        return 0

    def greaterpos_is_myself(self, msg):
        curRank = msg['curRank']
        if len(msg["handCards"]) == 1:  # 如果我们只剩一张牌，则返回该动作
            return 0
        if len(msg["handCards"]) == 2:  # 如果我们只剩两张牌，则优先考虑有没有对子
            for i in self.actionIndexList:
                if self.cards_number_count_list[0][0] == self.actionList[i][1] and \
                        self.cards_number_count_list[0][1] == 2:
                    self.cards_number_count_dict[i[1]] -= 2
                    return i
            return 0
        if len(msg["handCards"]) == 3:  # 如果我们只剩三张牌，则优先考虑有没有三张
            for i in self.actionIndexList:
                if self.cards_number_count_list[0][0] == self.actionList[i][1] and \
                        self.cards_number_count_list[0][1] == 3:
                    self.cards_number_count_dict[i[1]] -= 3
                    return i
            return 0


        # 对手的牌数只剩3张
        if self.opponent1_rest_cards == 3 or self.opponent2_rest_cards == 3:
            for i in self.actionIndexList:
                if self.actionList[i][0] == 'Trips':
                    pass
                else:
                    return self.order_of_play(msg)

        # 对手的牌数只剩2张
        if self.opponent1_rest_cards == 2 or self.opponent2_rest_cards == 2:
            for i in self.actionIndexList:
                if self.actionList[i][0] == 'Pair':
                    pass
                else:
                    return self.order_of_play(msg)
        # 对手的牌数只剩1张
        if self.opponent1_rest_cards == 1 or self.opponent2_rest_cards == 1:
            for i in self.actionIndexList:
                if self.actionList[i][0] == 'Single':
                    pass
                else:
                    return self.order_of_play(msg)

        return self.order_of_play(msg)
        # for i in self.actionIndexList:
        #     if self.actionList[i][0] in ['TwoTrips', 'ThreeWithTwo', 'ThreePair', 'Trips', 'Pair'] and \
        #             self.actionList[i] not in self.actionIndexList:
        #         return i
        # return 1

    # 队友是最大点数的策略
    def greaterpos_is_teammate(self, msg, flag):
        curRank = msg['curRank']  # 记录当前级数
        if flag == ONLY_BOMB:
            return 0
        elif flag == ONLY_SAME_TYPE or flag == SAME_TYPE_AND_BOMB:
            # 队友的牌足够大，那我们pass
            if msg['greaterAction'][1] in ['Q', 'K', 'A', curRank, 'B', 'R']:
                return 0
            elif msg['greaterAction'][0] == 'Straight' and msg['greaterAction'][2][4][1] in ['J', 'Q', 'K', 'A']:
                return 0
            else:
                if len(self.actionIndexList) == 1:
                    return 0
                # 队友的牌较小，那我们先过滤牌，再出相同的牌型
                for i in self.actionList[self.actionIndexList[1]][2]:
                    self.cards_number_count_dict[i[1]] -= 1
                return self.actionIndexList[1]
        else:
            pass

    # 对手是最大点数的策略
    def greaterpos_is_opponent(self, msg, flag):

        # 回合数较小时
        # if self.rounds <= self.ideal_round:
        if self.opponent1_rest_cards >= 18 or self.opponent2_rest_cards >= 18:
            if flag == ONLY_BOMB:
                return 0
            elif flag == ONLY_SAME_TYPE or flag == SAME_TYPE_AND_BOMB:
                if len(self.actionIndexList) == 1:
                    return 0
                for i in self.actionList[self.actionIndexList[1]][2]:
                    self.cards_number_count_dict[i[1]] -= 1
                return self.actionIndexList[1]
        # 回合数较大时
        else:
            # 对手的牌数只剩4张
            if self.opponent1_rest_cards == 4 or self.opponent2_rest_cards == 4:
                if flag == ONLY_BOMB:
                    return 0

            # 如果对面出单张，我们先出自己的单牌
            if msg['greaterAction'] == 'Single':
                for i in self.actionIndexList:
                    if self.actionList[i][0] == 'Single' and self.cards_number_count_dict[self.actionList[i][1]] == 1:
                        self.cards_number_count_dict[i[1]] -= 1
                        return i
                for i in self.actionIndexList:  # 然后出三张中的一张
                    if self.actionList[i][0] == 'Single' and self.cards_number_count_dict[self.actionList[i][1]] == 3:
                        self.cards_number_count_dict[i[1]] -= 1
                        return i
                for i in self.actionList:  # 然后出炸弹
                    if self.actionList[i][0] == 'Bomb':
                        if self.actionList[i][1] == 'JOKER':
                            pass
                        else:
                            self.cards_number_count_dict[i[1]] -= 4
                            return i
                self.cards_number_count_dict[i[1]] -= 1
                return 1  # 最后才拆对子

            if flag == ONLY_BOMB:
                for i in self.actionList[1][2]:
                    self.cards_number_count_dict[i[1]] -= 1
                return 1
            elif flag == ONLY_SAME_TYPE or flag == SAME_TYPE_AND_BOMB:
                if len(self.actionIndexList) == 1:  # 只有一个选择
                    return 0

                # 如果对方打对子，而我们只能用一对王出，那我们pass
                if msg['greaterAction'][0] == 'Pair' and \
                        (self.actionList[self.actionIndexList[1]][1] == 'B' or self.actionList[self.actionIndexList[1]][1] == 'R'):
                    return 0

                for i in self.actionList[self.actionIndexList[1]][2]:
                    self.cards_number_count_dict[i[1]] -= 1
                return self.actionIndexList[1]


    def type_flag(self, actionList) -> int:

        # 如果第二个动作为炸弹，则说明只有炸弹（第一个动作恒为pass）
        if actionList[1][0] in ['Bomb', 'StraightFlush']:
            return ONLY_BOMB
        else:
            for i in actionList:
                # 在第二个动作不为炸弹的情况下，如果动作列表里面存在炸弹
                if i[0] in ['Bomb', 'StraightFlush']:
                    return SAME_TYPE_AND_BOMB
            # 在第二个动作不为炸弹的情况下，没有炸弹，则只有相同类型的牌
            return ONLY_SAME_TYPE



    def parse(self, msg, rounds, my_pos):
        self.handCards = msg['handCards']
        # self.hongTaoRank = 'H' + msg['curRank']
        self.agent_pos = my_pos
        self.rounds = rounds

        # 判断对手的位置
        if self.agent_pos == 0 or self.agent_pos == 2:
            opponent1 = 1
            opponent2 = 3
        else:
            opponent1 = 0
            opponent2 = 2

        self.opponent1_rest_cards = msg["publicInfo"][opponent1]["rest"]    # 对手1剩余的手牌
        self.opponent2_rest_cards = msg["publicInfo"][opponent2]["rest"]    # 对手2剩余的手牌
        if self.render:
            print("对方剩余的手牌数量:", self.opponent1_rest_cards,  self.opponent2_rest_cards)
        self.actionList = msg["actionList"]
        self.act_range = msg["indexRange"]

        self.actionIndexList = self.filterActionList()

        # 根据算法选择动作

        action_final_index = self.algorithm(msg)
        if self.render:
            print("当前动作列表为{}".format(self.actionList))
            print("-" * 20)
            print("当前回合数为:{}   可选动作范围为:0至{}   算法认为应选择{}".format(
                self.rounds, self.act_range, action_final_index))

        return action_final_index
