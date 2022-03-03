import argparse
import torch
import random

from copy import deepcopy

class demo:
    def __init__(self) -> None:
        self.buff = []
    
    def append(self, a):
        self.buff.append(deepcopy(a))


parser = argparse.ArgumentParser()

parser.add_argument('-d', default=None, type=str)

state = torch.load(r"E:\Project\NUAA-guandan\model\checkpoints_2022_2_13_13_48_5\2022_2_13_13_48_9_value_-0.0.pth")

a = {1 : 1, 2 : 2}

print(id(a))

d = demo()

a[1] = 1
a[2] = 5

d.append(a)

a[1] = 4
a[2] = 7

d.append(a)

print(d.buff)