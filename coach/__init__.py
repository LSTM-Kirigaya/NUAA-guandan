from importlib import import_module
import os, sys
from pprint import pprint

sys.path.append(os.path.abspath('.'))

_ROOT_FOLDER = "coach"
_REGISTER_CLIENT = dict()

for folder in os.listdir(_ROOT_FOLDER):
    if folder.endswith("py") or folder.startswith('__'):
        pass
    else:
        module = import_module(name="{}.{}.client".format(_ROOT_FOLDER, folder))
        _REGISTER_CLIENT[folder] = module.Main

def LoadCoach(coach_name):
    if coach_name in _REGISTER_CLIENT:
        return _REGISTER_CLIENT[coach_name]
    else:
        from colorama import Back, Style
        print(Back.RED, "{}不在已注册的智能体中, 已注册的智能体名称如下:".format(coach_name), Style.RESET_ALL)
        pprint(list(_REGISTER_CLIENT.keys()))
        print()
        exit(-1)

