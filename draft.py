import argparse


parser = argparse.ArgumentParser()

parser.add_argument('-d', default=None, type=int)

args = vars(parser.parse_args())

print(type(args["d"]))