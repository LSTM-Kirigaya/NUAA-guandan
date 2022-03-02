
def getval(card, rank, has):
    des = -1
    if card[0] == 'S':
        des = 0
    elif card[0] == 'H':
        des = 1
    elif card[0] == 'C':
        des = 2
    elif card[0] == 'D':
        des = 3
    if card[1] == 'T':
        val = 9
        index = 8
    elif card[1] == 'J':
        val = 10
        index = 9
    elif card[1] == 'Q':
        val = 11
        index = 10
    elif card[1] == 'K':
        val = 12
        index = 11
    elif card[1] == 'A':
        val = 13
        index = 12
    elif card[1] == 'B' or card[1] == 'R':
        val = 15
        index = 13
    else:
        val = int(card[1])-1
        index = int(card[1])-2
    if card[1] == rank:
        val = 14
    if card == 'SB':
        if has[0][13] == 2 and has[1][13] == 2:
            val *= 100
        elif has[0][13] == 2 and has[1][13] != 2:
            val += 20
    elif card == 'HR':
        if has[0][13] == 2 and has[1][13] == 2:
            val *= 100
        elif has[0][13] != 2 and has[1][13] == 2:
            val += 20
    elif card[0] == 'H' and card[1] == rank:
        val = 160
    else:
        ans = 0
        for num in range(index-4, index+1):
            if num >= -1 and num+4 <= 12:
                if num == -1:
                    if has[des][12] >= 1 and has[des][0] >= 1 and has[des][1] >= 1 and has[des][2] >= 1 \
                            and has[des][3] >= 1:
                        ans = 140+val
                else:
                    if has[des][num] >= 1 and has[des][num+1] >= 1 and has[des][num+2] >= 1 and has[des][num+3] >= 1 \
                            and has[des][num+4] >= 1:
                        ans = 140+val
        if has[4][index] <= 3:
            val += 20 * (has[4][index]-1)
        elif has[4][index] == 4:
            val += 80
        elif has[4][index] == 5:
            val += 120
        else:
            val += (40 * (has[4][index]-5) + 140)
        if val < ans:
            val = ans
    return val


def cac(gain, value, poss):
    return gain*(1 + poss)/value


def solve(msg, case):
    zero_s_cards = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    zero_h_cards = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    zero_c_cards = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    zero_d_cards = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    zero_number_cards = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    zero_rank_cards = [0, 0]

    has = [zero_s_cards, zero_h_cards, zero_c_cards, zero_d_cards, zero_number_cards, zero_rank_cards]
    now_rank = msg["curRank"]
    for card in msg["handCards"]:
        des = -1
        if card[0] == 'S':
            des = 0
        elif card[0] == 'H':
            des = 1
        elif card[0] == 'C':
            des = 2
        elif card[0] == 'D':
            des = 3
        if card[1] == 'T':
            has[des][8] += 1
            has[4][8] += 1
        elif card[1] == 'J':
            has[des][9] += 1
            has[4][9] += 1
        elif card[1] == 'Q':
            has[des][10] += 1
            has[4][10] += 1
        elif card[1] == 'K':
            has[des][11] += 1
            has[4][11] += 1
        elif card[1] == 'A':
            has[des][12] += 1
            has[4][12] += 1
        elif card[1] == 'B':
            has[des][13] += 1
        elif card[1] == 'R':
            has[des][13] += 1
        else:
            has[des][int(card[1]) - 2] += 1
            has[4][int(card[1]) - 2] += 1

    act_score = []

    for action in msg["actionList"]:
        if action[0] == "Single":
            values = []
            for one in action[2]:
                values.append(getval(one, now_rank, has))
            value = max(values)
            poss = 1
            score = cac(1, value, poss)
            act_score.append(score)

        elif action[0] == "Pair":
            values = []
            for one in action[2]:
                values.append(getval(one, now_rank, has))
            value = max(values)
            poss = 1
            score = cac(2, value, poss)
            act_score.append(score)

        elif action[0] == "Trips":
            values = []
            for one in action[2]:
                values.append(getval(one, now_rank, has))
            value = max(values)
            poss = 1
            score = cac(3, value, poss)
            act_score.append(score)

        elif action[0] == "ThreePair":
            values = []
            for one in action[2]:
                values.append(getval(one, now_rank, has))
            value = max(values)
            poss = 1
            score = cac(6, value, poss)
            act_score.append(score)

        elif action[0] == "ThreeWithTwo":
            values = []
            for one in action[2]:
                values.append(getval(one, now_rank, has))
            value = (max(values) + min(values))/2
            poss = 1
            score = cac(5, value, poss)
            act_score.append(score)

        elif action[0] == "TwoTrips":
            values = []
            for one in action[2]:
                values.append(getval(one, now_rank, has))
            value = max(values)
            poss = 1
            score = cac(6, value, poss)
            act_score.append(score)

        elif action[0] == "Straight":
            values = []
            for one in action[2]:
                values.append(getval(one, now_rank, has))
            value = sum(values)
            poss = 1
            score = cac(5, value, poss)
            act_score.append(score)

        elif action[0] == "StraightFlush":
            values = []
            for one in action[2]:
                values.append(getval(one, now_rank, has))
            value = max(values)
            poss = 1
            score = cac(5, value, poss)
            act_score.append(score)

        elif action[0] == "Bomb":
            values = []
            for one in action[2]:
                values.append(getval(one, now_rank, has))
            value = max(values)
            poss = 1
            score = cac(len(values), value, poss)
            act_score.append(score)

        elif action[0] == "PASS":
            if msg["greaterPos"] == case:
                if msg["publicInfo"][case]['rest'] <= 6:
                    value = 1
                    poss = 1
                    score = cac(1, value, poss)
                    act_score.append(score)
                else:
                    if msg["greaterAction"][0] == "Single":
                        value = 25
                        poss = 1
                        score = cac(2, value, poss)
                        act_score.append(score)
                    elif msg["greaterAction"][0] == "Pair":
                        value = 65
                        poss = 1
                        score = cac(4, value, poss)
                        act_score.append(score)
                    else:
                        value = 1
                        poss = 1
                        score = cac(1, value, poss)
                        act_score.append(score)
            else:
                value = 1
                poss = 1
                score = cac(0, value, poss)
                act_score.append(score)

        elif action[0] == "back":
            values = []
            for one in action[2]:
                values.append(getval(one, now_rank, has))
            value = max(values)
            poss = 1
            score = cac(1, value, poss)
            act_score.append(score)

        elif action[0] == "tribute":
            values = []
            for one in action[2]:
                values.append(getval(one, now_rank, has))
            value = max(values)
            poss = 1
            score = cac(1, value, poss)
            act_score.append(score)

    return act_score.index(max(act_score))
