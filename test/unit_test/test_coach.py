# -*- coding: utf-8 -*-
# @Time       : 2022/2/20
# @Author     : Zhelong Huang
# @File       : test_coach.py
# @Description: Test

# 测试coach中的智能体是否可以正常运转
# 第一组测试:按照顺序进行，每次测试中，都让四个玩家使用完全相同的coach
# 第二组测试:混排测试，每个玩家的coach都随机抽取
# 每组测试的每个环节都使用10个游戏次数

import os, sys
from tqdm import tqdm
from colorama import Back, Style
from datetime import datetime

sys.path.append(os.path.abspath('.'))
from coach import _REGISTER_CLIENT

PYTHON_INTERPRET = "python"
LAUNCH_FILE = "./launch/launch.py"
LOG_DIR = "test/log"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

all_coaches = list(_REGISTER_CLIENT.keys())

def test_coach():
    now = datetime.now()
    test_time = "{}_{}_{}_{}_{}_{}".format(
        now.year, now.month, now.day, now.hour, now.minute, now.second
    )
    coaches_num = len(all_coaches)
    iter_wrapper = tqdm(range(coaches_num))
    for i in iter_wrapper:
        client = all_coaches[i]
        iter_wrapper.set_description_str("测试 {}".format(client))
        try:
            ret = os.system("{} -u {} -pc1 {} -pc2 {} -pc3 {} -pc4 {}".format(
                PYTHON_INTERPRET, LAUNCH_FILE, client, client, client, client
            ))
        except BaseException as e:
            print(Back.RED, "出现错误", Style.RESET_ALL)
            with open(LOG_DIR + "/" + test_time + ".log", "a", encoding="utf-8") as fp:
                fp.write(str(e))
                fp.write("\n")

test_coach()