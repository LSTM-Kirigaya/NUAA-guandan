# -*- coding: utf-8 -*-
_POS = 1

import json
from ws4py.client.threadedclient import WebSocketClient
from state import State
from action import Action
from ai_action import MLPAction
from coach import LoadCoach
import argparse


arg = argparse.ArgumentParser()
arg.add_argument('-r', '--render', default=True)
arg.add_argument('-c', '--client', default="Demo")
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
