# -*- coding: utf-8 -*-
# @Time       : 2020/10/16 23:55
# @Author     : Floating
# @File       : AIAction.py
# @Description: ai动作类

from random import randint
import random

TYPE_LIST=[ 
    "Single",
    "Pair",
    "Trips",
    "ThreePair",
    "ThreeWithTwo",
    "TwoTrips",
    "Straight"
]
# 根据牌的类型给出其映射序号
card_type_mapping = {
    "Single": 0,
    "Pair": 1,
    "Trips": 2,
    "ThreePair": 3,
    "ThreeWithTwo": 4,
    "TwoTrips": 5,
    "Straight": 6,
    "Bomb": 7,
    "StraightFlush": 8,
    "PASS": 9
}

# 我们认为的大牌型
big_type_cards = [
    "Bomb", "StraightFlush","SA", "HA", "CA", "DA","SB","HR"
]

# 牌到点数的映射
card2num = {
    "SA": 1, "HA": 1, "CA": 1, "DA": 1, "A": 1,
    "S2": 2, "H2": 2, "C2": 2, "D2": 2, "2": 2,
    "S3": 3, "H3": 3, "C3": 3, "D3": 3, "3": 3,
    "S4": 4, "H4": 4, "C4": 4, "D4": 4, "4": 4,
    "S5": 5, "H5": 5, "C5": 5, "D5": 5, "5": 5,
    "S6": 6, "H6": 6, "C6": 6, "D6": 6, "6": 6,
    "S7": 7, "H7": 7, "C7": 7, "D7": 7, "7": 7,
    "S8": 8, "H8": 8, "C8": 8, "D8": 8, "8": 8,
    "S9": 9, "H9": 9, "C9": 9, "D9": 9, "9": 9,
    "ST": 10, "HT": 10, "CT": 10, "DT": 10, "T": 10,
    "SJ": 11, "HJ": 11, "CJ": 11, "DJ": 11, "J": 11,
    "SQ": 12, "HQ": 12, "CQ": 12, "DQ": 12, "Q": 12,
    "SK": 13, "HK": 13, "CK": 13, "DK": 13, "K": 13,
    "SB": 14,  # 小王映射成14，大王映射成15
    "HR": 15,
    "PASS": 0  # PASS 映射成0
}


# 一个全场牌的列表

allCards=[ 
    "SA", "HA", "CA", "DA",
    "S2", "H2", "C2", "D2",
    "S3", "H3", "C3", "D3",
    "S4", "H4", "C4", "D4",
    "S5", "H5", "C5", "D5",
    "S6", "H6", "C6", "D6",
    "S7", "H7", "C7", "D7",
    "S8", "H8", "C8", "D8",
    "S9", "H9", "C9", "D9",
    "ST", "HT", "CT", "DT",
    "SJ", "HJ", "CJ", "DJ",
    "SQ", "HQ", "CQ", "DQ",
    "SK", "HK", "CK", "DK",
    "SB", "HR",

    "SA", "HA", "CA", "DA",
    "S2", "H2", "C2", "D2",
    "S3", "H3", "C3", "D3",
    "S4", "H4", "C4", "D4",
    "S5", "H5", "C5", "D5",
    "S6", "H6", "C6", "D6",
    "S7", "H7", "C7", "D7",
    "S8", "H8", "C8", "D8",
    "S9", "H9", "C9", "D9",
    "ST", "HT", "CT", "DT",
    "SJ", "HJ", "CJ", "DJ",
    "SQ", "HQ", "CQ", "DQ",
    "SK", "HK", "CK", "DK",
    "SB", "HR",   ]


class AIAction(object):

    def __init__(self, render):
        self.actionList = []  # 当前的动作列表
        self.act_range = -1  # 动作索引范围
        self.restCards = []  # agent剩余手牌
        self.starting_threshold = 5  # 开局阈值，在该值之前AI认为是“刚刚开局”
        self.episode_rounds = 0  # 回合数
        self.agent_pos = None  # 位置
        self.render = render

    # 统计列表中的词频，并返回字典
    def count(self, list):
        target_dict = {}
        for item in list:
            item = card2num[item]
            target_dict[item] = target_dict.get(item, 1) + 1
        return target_dict

    # 函数功能为判断选定的牌型是否造成了拆牌，若造成拆牌返回True，没有拆牌返回False
    def will_choice_break_other(self, msg, action_index):       #传入的参数分别代表选中条目的序号
        
        """
        :param msg: 全局信息
        :param choose_card_trips: agent选择的卡牌三元组
        :param rest_cards: agent剩余卡牌
        :return:
        """
        rest_cards=msg["handCards"]
        choose_card_trips=msg["actionList"][action_index]

        card_type = choose_card_trips[0]    #记录牌型
        #cards_num = choose_card_trips[1]    #牌的点数 顺子，连对等以最小的牌型作为点数
        cards = choose_card_trips[2]        #cards提取的是卡牌列表

        card_count = self.count(rest_cards) # 获取剩余卡牌的各点数卡牌数量
        
        #不知道为什么每一张都多一个，先减掉
        for item in card_count :
            card_count[item]-=1
        count =0
        # 判断卡牌类型
        if card_type == "Single":
            count = 1                       #count 记录的是卡牌数量
        elif card_type == "Pair":
            count = 2
        elif card_type == "Trips":
            count = 3
        elif card_type == "ThreeWithTwo":
            count = 4                       #前三个count是记录卡牌数量，从第四个开始为标记牌型，从而进入不同的分支
        elif card_type == "ThreePair":
            count = 5
        elif card_type == "TwoTrips":
            count = 6
        elif card_type == "Straight":       #顺子和同花顺是现在没有判断的两个
            count = 7
        elif card_type == "StraightFlush":
            count = 8
        elif card_type == "Bomb":
            count = 9
        
        flag = False
    
        if count in [1,2,3]:                   #点数相同牌型的进行拆牌判断        
            cur_card_num = card2num[cards[0]]  #记录牌型映射的数字
            if self.render:
                print (card_count[card2num[cards[0]]])
                print (count)
            if (cur_card_num == 1 or cur_card_num == card2num[msg['curRank']]) and card_count[card2num[cards[0]]] == 3 and (count == 1 or count == 2):           
                flag = False                             #single和pair如果拆了A和Rank牌,且这个牌有三张，那么我们算作不拆牌
    
            elif (cur_card_num == 1 or cur_card_num == card2num[msg['curRank']]) and card_count[card2num[cards[0]]] == 2 and (count == 1):           #single和pair如果拆了A和Rank牌,且这个牌有三张，那么我们算作不拆牌
                
                flag = False                             #同上，single拆pair不算拆牌
            
            elif card_count[card2num[cards[0]]] == count:  # 如果卡牌数和剩余数量相等  ***只能从牌映射到点数
                if self.render:
                    print('pln')
                flag = False
            
            else:
                flag = True
    
        elif count == 4:                       #三带二拆牌判断
            
            cur_card_num1 = card2num[cards[0]]  #记录三带二其中三张牌部分映射的数字
            cur_card_num2 = card2num[cards[3]]  #记录三带二其中两张牌部分映射的数字
            if card_count[cur_card_num1]>=4 or card_count[cur_card_num2]>=3:
                flag = True
            else :
                flag = False
            pass
    
        elif count == 5:                       #三连对拆牌判断，只要不拆炸弹和钢板即可
            
            cur_card_num1 = card2num[cards[0]]  #记录三连对第一张牌映射的数字
            cur_card_num2 = cur_card_num1 + 1
            cur_card_num3 = cur_card_num1 + 2
            
            if cur_card_num3 > 13:
                cur_card_num3 %= 13               #这是QKA的情况，循环回去
            
            if (card_count[cur_card_num1] >=4) or (card_count[cur_card_num2] >=4) or (card_count[cur_card_num3] >=4) :
                flag = True
    
            elif  (card_count[cur_card_num1]>=3 and card_count[cur_card_num2]>=3) or (card_count[cur_card_num1]>=3 and card_count[cur_card_num3]>=3) or (card_count[cur_card_num3]>=3 and card_count[cur_card_num2]>=3):
                
                flag = True
            
            else:
                flag = False
            pass
    
        elif count == 6:                       #判断钢板会不会拆炸弹
            cur_card_num1 = card2num[cards[0]]  #记录三连对第一张牌映射的数字
            cur_card_num2 = cur_card_num1 + 1
            
            if cur_card_num2 > 13:
                cur_card_num2%=13 
            
            if card_count[cur_card_num1]>=4 or card_count[cur_card_num2]>=4:
                flag = True
            else:
                flag = False
            pass
    
        elif count == 7:                       #判断顺子是否拆牌
            
            cur_card_num1 = card2num[cards[0]] #记录顺子的第一张牌
            cur_card_list = [cur_card_num1]    #构造出来顺子中映射后的点数
            
            for index in range (1,5):
                now_num=cur_card_num1+index
                if now_num > 13:
                    now_num %= 13 
                cur_card_list.append(now_num)
    
            cnt1 = 0 #记录拆下来几张单牌
            cnt2 = 0 #记录拆下来几个对子
            for item in cur_card_list:
                if  card_count[item] >= 4:
                    flag = True 
                    break
                elif card_count[item]==2:
                    cnt1+=1
                elif card_count[item]==3:
                    cnt2+=1
                else:
                    pass
    
            if cnt1>=3 or cnt2 >= 3 :
                flag=True
                pass
    
            elif cnt1==1 and cnt2 <=2:
                flag=False
                pass
            elif cnt1==2 and cnt2 <=1:
                flag=False
                pass
    
            else:
                flag=True
                pass
            pass
    
        elif count == 8:                       #判断顺子是否拆牌
    
            cur_card_num1 = card2num[cards[0]] #记录顺子的第一张牌
            cur_card_list = [cur_card_num1]    #构造出来顺子中映射后的点数
            
            for index in range (1,5):
                now_num=cur_card_num1+index
                if now_num > 13:
                    now_num %= 13 
                cur_card_list.append(now_num)
    
            cnt1 = 0 #记录拆下来几张单牌
            cnt2 = 0 #记录拆下来几个对子
            for item in cur_card_list:
                if  card_count[item] >= 4:
                    flag = True 
                    break
                elif card_count[item]==2:
                    cnt1+=1
                elif card_count[item]==3:
                    cnt2+=1
                else:
                    pass
    
            if cnt1 >= 3 or cnt2 >= 3 :
                flag=True
                pass
    
            elif cnt1==1 and cnt2 <=2:
                flag=False
                pass
            elif cnt1==2 and cnt2 <=1:
                flag=False
                pass
    
            else:
                flag=True
                pass
            pass
    
        elif count == 9:                       #炸弹拆牌判断
            
            cur_card_num = card2num[cards[0]]  #记录牌型映射成的点数
            
            if card_count[cur_card_num] <= len(cards):  # 如果剩余卡牌小于等于组合牌数，则是全部数量的牌或利用了逢人配，返回为False，未拆牌
                #左边是剩余手牌，右边是当前选择的有多少张牌
                flag = False
            else:
                flag = True
            return flag
        
        else:
            #如果不是，那么默认没有拆牌
            pass
    
        return flag
       
    
    #回手牌策略,根据message，返回可选牌型的列表
    def  static_back_hand(self,msg):

        rest_cards=msg["handCards"]         #剩余手牌
        card_count = self.count(rest_cards) # 获取剩余卡牌的各点数卡牌数量
        
        for item in card_count :
            card_count[item]-=1
        
        #可选牌型列表
        choice_list=[]
        
        single_big_card = [1,14,15,card2num[msg["curRank"]]] #认为single中比较大的牌
        pair_big_card = [1,12,13,card2num[msg["curRank"]]]   #下边同理
        trips_big_card = [1,11,12,13,card2num[msg["curRank"]]]

        for item in card_count:

            if card_count[item]==1:
                if item in single_big_card:
                    choice_list.append("Single")

            elif card_count[item]==2:
                if item in pair_big_card:
                    choice_list.append("Single")
                    choice_list.append("Pair")

            elif card_count[item]==3:
                if item in trips_big_card:
                    choice_list.append("Trips",)
                    choice_list.append("ThreeWithTwo")
                    choice_list.append("TwoTrips")

        return list(set(choice_list))

    def back_strategy(self,msg):
        
        rest_cards=msg["handCards"]
        card_count = self.count(rest_cards) # 获取剩余卡牌的各点数卡牌数量
        
        for index, item in enumerate (msg["actionList"]):
            if card_count[card2num[item[2][0]]]==1 and card2num[item[2][0]]<=10 and card2num[item[2][0]]!= card2num[ msg["curRank"]] :
                return index

        for index, item in enumerate (msg["actionList"]):
            if self.will_choice_break_other(msg,index) == False and card2num[item[2][0]]<= 10 and card2num[item[2][0]]!= card2num[ msg["curRank"]]:
                return index
        return 0
        
    # 策略算法预测
    
    def strategy_predict(self, msg):

        if msg["stage"]=="back":
            return self.back_strategy(msg)
           

    
        if msg["indexRange"] == 0:  # 别无选择
            return 0

        # 接牌
        if self.actionList[0][0] == "PASS":
            if msg["greaterPos"] == (self.agent_pos + 2) % 4:  # 如果最大牌是队友出的
                return self.greaterIsPantner(msg)
            else:  # 如果最大牌是对手出的
                return self.greaterIsEmery(msg)

        # 出牌
        else:
            return self.active_play_out(msg)


    # 当前最大是队友时，我们的接牌策略是
    def greaterIsPantner(self, msg):
        if msg["greaterAction"][0] in big_type_cards:  # 队友出的牌型属于大牌
            return 0  #这是后我们选择不出
        
        else:  # 队友出的牌型属于小牌，这个时候我们要选一个相应的小牌出去
            return 1

    # 当前最大是对手时，我们的接牌策略,这里我们要分张数进行讨论
    def greaterIsEmery(self, msg):
        
        emery_rest1=msg["publicInfo"][(self.agent_pos+1)%4]     #提取出对手出牌信息的字典
        emery_rest2=msg["publicInfo"][(self.agent_pos+3)%4]
        min_rest=min(emery_rest1["rest"],emery_rest2["rest"])
        
        if min_rest >= 10:
            temp = randint(0,10)
            if temp%4==0:
                return randint(1,max(msg["indexRange"]//4, 1))
            else:
                return 1
      
        else: 
            now_type= msg["greaterAction"][0]
            if now_type in TYPE_LIST:
                my_same_type = []

                for index, action in enumerate(msg["actionList"]):
                    if action[0] == now_type:
                        my_same_type.append({
                            "action" : action,
                            "index" : index
                        })

                if len(my_same_type) == 0:      # 如果列表为空，也就是我方动作列表没有与对手相同的牌型
                    e = random.random()
                    if e < 0.3:         # 0.3的概率出牌
                        return 1
                    else:
                        return 0

                else:           # 如果有牌型

                    type_num = len(my_same_type)
                    no_break_action = []
                    break_action = []

                    for item in my_same_type:
                        if (self.will_choice_break_other(msg, item["index"])):
                            break_action.append(item)
                        else:
                            no_break_action.append(item)

                    if len(no_break_action) == 0:       # 所有的动作都会拆牌
                        return 0
                    else:       # 存在不拆牌的
                        return no_break_action[0]["index"]


            else:
                e = random.random()
                if e < 0.7:         # 0.7的概率出牌
                    return 1
                else:
                    return 0


    #这个函数帮助我们进行优先选择，需要传入一个类型列表，会返回经过检验拆牌的最小的合理选择
    def FirstChoice (self,msg,Choice_list):
        for index, action in enumerate(msg["actionList"]):
            if action[0] in Choice_list and self.will_choice_break_other(msg, index) == False:
                return index
        return -1
    
    #当我们主动出牌时
    def active_play_out(self, msg):
        
        emery_rest1 = msg["publicInfo"][(self.agent_pos+1)%4]     #提取出对手出牌信息的字典
        emery_rest2 = msg["publicInfo"][(self.agent_pos+3)%4]
        min_rest = min(emery_rest1["rest"],emery_rest2["rest"])   #提取出场上对手牌数最少的值
              
        if min_rest >10 :
            #优先选择回手牌策略
            can_choice=self.static_back_hand(msg)
            if "Single" in can_choice:
                flag = self.FirstChoice(msg,["Single"])
                if flag != -1:
                    return flag

            if "Pair" in can_choice:
                flag = self.FirstChoice(msg,["Pair"])
                if flag != -1:
                    return flag

            if "ThreeWithTwo" in can_choice:
                flag = self.FirstChoice(msg,["ThreeWithTwo"])
                if flag != -1:
                    return flag

            if "Trips" in can_choice:
                flag=self.FirstChoice(msg,["Trips"])
                if flag != -1:
                    return flag
            
            #再根据优先级进行选择 

            Choice_list1 = [ "ThreeWithTwo","TwoTrips"]
            Choice_list2 = [ "ThreePair"]
            Choice_list3 = [ "Trips"]
            Choice_list4 = [ "Straight"]
            Choice_list5 = [ "Pair"]
            Choice_list6 = [ "Single"]

            flag = self.FirstChoice(msg,Choice_list1)
            if flag != -1 :
                return flag

            flag = self.FirstChoice(msg,Choice_list2)
            if flag != -1 :
                return flag
            
            flag = self.FirstChoice(msg,Choice_list3)
            if flag != -1 :
                return flag

            flag = self.FirstChoice(msg,Choice_list4)
            if flag != -1 :
                return flag

            flag = self.FirstChoice(msg,Choice_list5)
            if flag != -1 :
                return flag

            flag = self.FirstChoice(msg,Choice_list6)
            if flag != -1 :
                return flag
            
            return randint(1,msg["indexRange"])

        #elif min_rest >=10 and min_rest <=17:

        elif min_rest <= 10:
            
            if min_rest == 1: #只剩一张牌了
                for index in range(len(msg['actionList'])):
                    if msg['actionList'][index][0] != "Single":
                        if self.will_choice_break_other(msg,index) == False:
                            return index
                return randint(0,msg['indexRange'])
            
            elif min_rest == 2: #最少的只剩下两张牌了
                
                Choice_list1 = [ "TwoTrips","Straight","ThreePair","ThreeWithTwo","Trips"]
                Choice_list2 = ["Single"]

                flag = self.FirstChoice(msg,Choice_list1)
                if flag != -1 :
                    return flag
                flag = self.FirstChoice(msg,Choice_list2)
                if flag != -1 :
                    return flag

                return randint(1,1000)%msg["indexRange"]

            elif min_rest == 3:#最少牌的对手只剩三张牌
                
                Choice_list1 = [ "ThreePair","ThreeWithTwo","TwoTrips","Straight"]
                Choice_list2 = [ "Pair"]
                Choice_list3 = [ "Single"]
                Choice_list4 = [ "Trips"]

                flag = self.FirstChoice(msg,Choice_list1)
                if flag != -1 :
                    return flag
                flag = self.FirstChoice(msg,Choice_list2)
                if flag != -1 :
                    return flag
                flag = self.FirstChoice(msg,Choice_list3)
                if flag != -1 :
                    return flag
                flag = self.FirstChoice(msg,Choice_list4)
                if flag != -1 :
                    return flag

                return randint(1,msg["indexRange"])

            elif min_rest==4 or min_rest==5: #如果剩余了四张或者五张牌

                Choice_list1 = [ "TwoTrips","ThreePair","Straight"]
                Choice_list2 = [ "Trips"]
                Choice_list3 = [ "ThreeWithTwo"]
                Choice_list4 = [ "Pair"]
                Choice_list5 = [ "Single"]

                flag = self.FirstChoice(msg,Choice_list1)
                if flag != -1 :
                    return flag

                flag = self.FirstChoice(msg,Choice_list2)
                if flag != -1 :
                    return flag
                
                flag = self.FirstChoice(msg,Choice_list3)
                if flag != -1 :
                    return flag

                flag = self.FirstChoice(msg,Choice_list4)
                if flag != -1 :
                    return flag

                flag = self.FirstChoice(msg,Choice_list5)
                if flag != -1 :
                    return flag
                
                return randint(1,msg["indexRange"])

            elif min_rest>=6 or min_rest<=10:

                Choice_list1 = [ "ThreeWithTwo","TwoTrips"]
                Choice_list2 = [ "ThreePair"]
                Choice_list3 = [ "Trips"]
                Choice_list4 = [ "Straight"]
                Choice_list5 = [ "Pair"]
                Choice_list6 = [ "Single"]

                flag = self.FirstChoice(msg,Choice_list1)
                if flag != -1 :
                    return flag

                flag = self.FirstChoice(msg,Choice_list2)
                if flag != -1 :
                    return flag
                
                flag = self.FirstChoice(msg,Choice_list3)
                if flag != -1 :
                    return flag

                flag = self.FirstChoice(msg,Choice_list4)
                if flag != -1 :
                    return flag

                flag = self.FirstChoice(msg,Choice_list5)
                if flag != -1 :
                    return flag

                flag = self.FirstChoice(msg,Choice_list6)
                if flag != -1 :
                    return flag
                
                return randint(1,msg["indexRange"])

    def parse(self, msg, restCards, episode_rounds, agent_pos):
        self.restCards = restCards
        self.episode_rounds = episode_rounds
        self.agent_pos = agent_pos
        # 获取message中的内容
        self.actionList = msg["actionList"]
        self.act_range = msg["indexRange"]

        # 根据所选策略做出判断
        action_index = self.strategy_predict(msg)
        if self.render:
            print(self.actionList)  # 打印动作列表
            print("-" * 20)
            print("目前回合数:{}\t可选动作范围为:0至{}\tAI认为应该选择{}".format(
                self.episode_rounds, self.act_range, action_index
            ))

        # action_index = int(input("你认为应该的动作索引:"))
        return min(action_index, len(msg["actionList"] ) - 1)