# -*- coding: utf-8 -*-
# @Time       : 2022/2/20
# @Author     : Zhelong Huang
# @File       : client1.py
# @Description: client1
_POS = 1

import os, sys
sys.path.append(os.path.abspath('.'))
from coach import LoadCoach
import argparse


arg = argparse.ArgumentParser()
arg.add_argument('-r', '--render', default=False, type=bool)
arg.add_argument('-c', '--client', default="Demo")
arg.add_argument('-d', '--device', default="cpu")
arg.add_argument('--model',        default=None, type=str,  help="path of the model, is None")
arg.add_argument('--lr',           default=1e-3, type=float,help="learning rate of training model")
arg.add_argument('--save_interval',default=1000, type=int,  help="frequency of saving the model")
arg.add_argument('--log_interval', default=100,  type=int,  help="frequency of logging the situation of training")

args = vars(arg.parse_args())

CLIENT_ARGS = {
    'url' : 'ws://127.0.0.1:23456/game/client{}'.format(_POS),
    'render' : bool(int(args['render']))
}


if __name__ == '__main__':
    try:
        ws = LoadCoach(args['client'])(**CLIENT_ARGS)
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
