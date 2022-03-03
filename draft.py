import argparse
import torch
import random
import os
from copy import deepcopy


# TODO : 实现当模仿学习的 value 为 nan 时，自动重启 
def lock_value(value, model_root="./model", reverse=False):
    iter_obj = os.listdir(model_root)
    if reverse:
        iter_obj.reverse()
    for checkpoints in iter_obj:
        print(checkpoints)
        check_path = os.path.join(model_root, checkpoints)
        for pth in os.listdir(check_path):
            if pth.endswith("pth"):
                params = pth[:-4].split("_")
                if params[-2] == "value" and float(params[-1]) == value:
                    return os.path.join(check_path, pth)

print(lock_value(433.502, reverse=True))