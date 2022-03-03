import torch
from torch import nn
from torch.nn import functional
import numpy as np
import os
from colorama import Back, Style
from datetime import datetime
from collections import deque
import random

DEVICE = "cpu"

card_color = ['S', 'H', 'C', 'D']
card_score = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
color2index = {v : i for i, v in enumerate(card_color)}
score2index = {v : i for i, v in enumerate(card_score)}
rank2index = {
    '2' : 0,
    '3' : 1,
    '4' : 2,
    '5' : 3,
    '6' : 4,
    '7' : 5,
    '8' : 6,
    '9' : 7,
    't' : 8,  'T' : 8, 
    'j' : 9,  'J' : 9,
    'q' : 10,  'Q' : 10,
    'k' : 11, 'K' : 11,
    'a' : 12, 'A' : 12
}

# embedding into a matrix shaped as 4 * 15
def encode_card(card_list):
    embedding_matrix = np.zeros((4, 15))
    embedding_matrix = torch.LongTensor(embedding_matrix)
    if card_list is None:
        return embedding_matrix
    for card in card_list:
        if   card == "PASS":      # 如果是PASS，那么用全0矩阵来表示这一次的行为
            return embedding_matrix
        if   card == "SB":        # 如果是小王，只需要在14列加数字
            embedding_matrix[3, 13] += 1
        elif card == "HR":       # 如果是大王，只需要在15列加数字
            embedding_matrix[3, 14] += 1
        else:                    # 否则按照规则映射
            color_index = color2index[card[0]]
            score_index = score2index[card[1]]
            embedding_matrix[color_index, score_index] += 1

    return embedding_matrix


# 简单处理一下发过来的数据
# ['PASS', 'PASS', 'PASS'] -> ['PASS', 'PASS', 'PASS']
# ['Straight', 'T', ['ST', 'SJ', 'SQ', 'SK', 'HA']]  -> ['ST', 'SJ', 'SQ', 'SK', 'HA']
def process_card_list(card):
    if card is None:
        return ('PASS', 'PASS', 'PASS')
    if card[0] == 'PASS':
        return card
    else:
        return card[-1]

# 从服务器传回的 message 中选出我们需要的信息并编码 
def encode_message(message):
    handcards_tensor = encode_card(message["handCards"])
    playArea_tensor  = [encode_card(process_card_list(card["playArea"])) for card in message["publicInfo"]]
    rest_tensor      = [card["rest"] for card in message["publicInfo"]]
    # 剩余手牌从0到27 一共28种状态
    try:
        rest_tensor      = functional.one_hot(torch.tensor(rest_tensor), num_classes=30)
    except:
        print(Back.RED, rest_tensor, Style.RESET_ALL)
    rank_tensor      = functional.one_hot(torch.tensor([rank2index[message["curRank"]]]), num_classes=13)
    # action_list      = [encode_card(card) if card[0] == "PASS" else encode_card(card[-1]) for card in message["actionList"]]
    return dict(
        handcards=handcards_tensor,
        playArea=playArea_tensor,
        rest_num=rest_tensor,
        rank_num=rank_tensor
        # action_list=action_list        
    )

# 状态整合方案一
def StateCatEmbedding(message):
    encode_info = encode_message(message)
    state_tensor = torch.cat((
        torch.flatten(encode_info["handcards"]),
        torch.flatten(encode_info["playArea"][0]),
        torch.flatten(encode_info["playArea"][1]),
        torch.flatten(encode_info["playArea"][2]),
        torch.flatten(encode_info["playArea"][3]),
        torch.flatten(encode_info["rest_num"]),
        torch.flatten(encode_info["rank_num"])
    ), dim=0)

    return state_tensor

def ActionEmbedding(message, action_index):
    action = message["actionList"][action_index]
    action_tensor = encode_card(process_card_list(action))
    return torch.flatten(action_tensor)

# 方案一的一个整合接口
def StateAndActionCatEmbedding(message, action_index):
    state_tensor  = StateCatEmbedding(message)
    action_tensor = ActionEmbedding(message, action_index)

    return torch.cat((
        torch.flatten(state_tensor), torch.flatten(action_tensor)
    ), dim=0)

def check_path(path : str, fail_text="") -> bool:
    if not os.path.exists(path):
        print(Back.RED, "文件/文件夹 {} 不存在!{}".format(path, fail_text), Style.RESET_ALL)
        exit(-1)
    else:
        return True

def now_str():
    now = datetime.now()
    UUD = "{}_{}_{}_{}_{}_{}".format(
        now.year, now.month, now.day, now.hour, now.minute, now.second
    )
    return UUD

class MemoryBuffer:
    def __init__(self) -> None:
        self.buffer = []

    def append(self, state_tuple):
        self.buffer.append(state_tuple)

    def clear(self):
        self.buffer.clear()
    
    def learn_from(self, gamma, optimizer, ValueNet):
        # 从后到前更新
        losses = []
        final_reward = None
        for i in range(len(self.buffer))[::-1]:
            frame = self.buffer[i]
            obs            = frame[0]
            history        = frame[1]
            act            = frame[2]
            reward         = frame[3]
            obs_next       = frame[4]
            actionListNext = frame[5]
            history_next   = frame[6]
            done           = frame[7]
            reward = torch.FloatTensor([reward])
            if done == False:
                print(reward, type(reward), reward.shape)
                final_reward = reward.item()
                # 计算max Q(S, *)
                q_values = []
                for action_card in actionListNext:
                    action = encode_card(process_card_list(action_card))
                    state_input = torch.cat((obs_next.flatten(), action.flatten()), dim=0).float().to(DEVICE)
                    state_action_input = state_input.unsqueeze(0).float().to(DEVICE)
                    q_value : torch.Tensor = ValueNet(state_action_input, history_next).sum()
                    q_values.append(q_value)

                max_q = torch.argmax(q_values)
                target = reward + gamma * max_q
            else:
                target = reward

            # 计算Q(St, At)
            action = encode_card(act)
            state_input = torch.cat((obs.flatten(), action.flatten()), dim=0).float().to(DEVICE)
            state_action_input = state_input.unsqueeze(0).float().to(DEVICE)
            q_value = ValueNet(state_action_input, history).sum()

            loss = torch.square(q_value - target)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            losses.append(loss.item())

        self.clear()
        return losses, final_reward

def lock_model_path(value, model_root="./model", keyword="value", reverse=True):
    iter_obj = os.listdir(model_root)
    if reverse:
        iter_obj.reverse()
    for checkpoints in iter_obj:
        check_path = os.path.join(model_root, checkpoints)
        for pth in os.listdir(check_path):
            if pth.endswith("pth"):
                params = pth[:-4].split("_")
                if params[-2] == keyword and float(params[-1]) == value:
                    return os.path.join(check_path, pth)
    return ""

if __name__ == "__main__":
    actionList = [['PASS', 'PASS', 'PASS'], ['Straight', 'T', ['ST', 'SJ', 'SQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'SJ', 'SQ', 'DK', 'HA']], ['Straight', 'T', ['ST', 'SJ', 'HQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'SJ', 'HQ', 'DK', 'HA']], ['Straight', 'T', ['ST', 'SJ', 'CQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'SJ', 'CQ', 'DK', 'HA']], ['Straight', 'T', ['ST', 'HJ', 'SQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'HJ', 'SQ', 'DK', 'HA']], ['Straight', 'T', ['ST', 'HJ', 'HQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'HJ', 'HQ', 'DK', 'HA']], ['Straight', 'T', ['ST', 'HJ', 'CQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'HJ', 'CQ', 'DK', 'HA']], ['Straight', 'T', ['ST', 'CJ', 'SQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'CJ', 'SQ', 'DK', 'HA']], ['Straight', 'T', ['ST', 'CJ', 'HQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'CJ', 'HQ', 'DK', 'HA']], ['Straight', 'T', ['ST', 'CJ', 'CQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'CJ', 'CQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'SJ', 'SQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'SJ', 'SQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'SJ', 'HQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'SJ', 'HQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'SJ', 'CQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'SJ', 'CQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'HJ', 'SQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'HJ', 'SQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'HJ', 'HQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'HJ', 'HQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'HJ', 'CQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'HJ', 'CQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'CJ', 'SQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'CJ', 'SQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'CJ', 'HQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'CJ', 'HQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'CJ', 'CQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'CJ', 'CQ', 'DK', 'HA']], ['Bomb', 'J', ['SJ', 'HJ', 'HJ', 'CJ']], ['StraightFlush', '7', ['S7', 'S8', 'S9', 'ST', 'SJ']], ['StraightFlush', '8', ['S8', 'S9', 'ST', 'SJ', 'SQ']], ['StraightFlush', '9', ['S9', 'ST', 'SJ', 'SQ', 'SK']]]
    
    for card_list in actionList:
        if card_list[0] == 'PASS':
            encode_card(card_list)
        else:
            encode_card(card_list[-1])