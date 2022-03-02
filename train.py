# -*- coding: utf-8 -*-
# @Time       : 2022/2/20 16:30
# @Author     : Zhelong Huang
# @File       : train.py
# @Description: training wrapping launch.py

import argparse
from util import check_path
import yaml, os

parser = argparse.ArgumentParser()
parser.add_argument(
    '-d', '--device', default="cpu",
    help="使用的运算设备, cpu或者cuda"
)
parser.add_argument(
    '-m', '--mode', default="il", 
    help="训练模式, il代表模仿学习, rl代表强化学习"
)
parser.add_argument(
    '-r', '--round', default=-1, type=int,
    help="对局的次数, 该参数也可以直接在launch/config.yaml中修改"
)
parser.add_argument(
    '--model', default=None,
    help="已经存在的一个神经网络参数模型, 用于持久化训练" 
)
parser.add_argument(
    '--lr', default=1e-3, type=float,
    help="learning rate of training model"
)
parser.add_argument(
    '--save_interval', default=1000, type=int, 
    help="frequency of saving the model"
)
parser.add_argument(
    '--log_interval', default=100, type=int,
    help="frequency of logging the situation of training"
)

for i in range(1, 5):
    parser.add_argument(
        "--agent{}".format(i), default="Demo",
        help="{}号玩家的 client 智能体, 只需要是注册在案的就行, 默认是Demo, 也就是随机采样".format(i)
    )


# 特殊的参数
parser.add_argument(
    "--show_all_agent", default="",
    help="展示所有注册的智能体, 参数为1"
)

if __name__ == "__main__":
    args = vars(parser.parse_args())
    
    if len(args["show_all_agent"]) > 0:
        from colorama import Back, Style
        from coach import _REGISTER_CLIENT
        from pprint import pprint
        print(Back.RED, "已注册的智能体名称如下:", Style.RESET_ALL)
        pprint(list(_REGISTER_CLIENT.keys()))
        print()
        exit(0)

    check_path("launch/config.yaml")
    check_path("launch/launch.py")

    # 修改YAML + 检查注册的客户端执行文件是否存在
    rounds = 10 if args["round"] == -1 else args["round"]

    with open("launch/config.yaml", "r", encoding="utf-8") as fp:
        config_dict = yaml.load(fp, yaml.Loader)

    # 1号玩家由训练程序代理，不需要检查
    for i in range(2, 5):
        check_path(config_dict["{}号玩家".format(i)], fail_text="如需修改客户端文件, 请在launch/config.yaml修改")

    # 根据输入参数配置
    config_dict["游玩次数"] = rounds
    if   args["mode"] == "il":
        config_dict["1号玩家"] = ".\\clients\\imitation_client.py"
    elif args["mode"] == "rl":
        config_dict["1号玩家"] = ".\\clients\\reinforment_client.py"

    with open("launch/config.yaml", "w", encoding="utf-8") as fp:
        yaml.dump(config_dict, fp, Dumper=yaml.Dumper, allow_unicode=True)

    ret = os.system("python -u ./launch/launch.py -d {} --model {} --lr {} --save_interval {} --log_interval {}".format(
        args["device"],
        args["model"],
        args["lr"],
        args["save_interval"],
        args["log_interval"]
    ))