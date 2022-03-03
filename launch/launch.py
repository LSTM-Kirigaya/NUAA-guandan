from typing import List
import yaml
from prettytable import PrettyTable
from multiprocessing import Process
import os, argparse, sys
from colorama import Back, Style
from time import sleep

sys.path.append(os.path.abspath('.'))
from coach import LoadCoach

parser = argparse.ArgumentParser()
parser.add_argument(
    '-m', '--mode', default="il", 
    help="训练模式, il代表模仿学习, rl代表强化学习"
)
parser.add_argument(
    '-d', '--device', default="cpu",
    help="使用的运算设备, cpu或者cuda"
)
parser.add_argument(
    '--model', default=None, type=str,
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
        help="{}号玩家的client, 只需要是注册在案的就行"
    )
parser.add_argument(
    '--epsilon', default=0.1, type=float,
    help="epislon-greed strategy probility"
)
parser.add_argument(
    '--gamma', default=0.98, type=float,
    help="decount factor when doing reinforcement learning"
)


class ServeProcess(Process):
    PLATFORM = "WINDOWS"
    def __init__(self, path, port):
        super(ServeProcess, self).__init__()
        if isinstance(path, str) and isinstance(port, int):
            self.path = path
            self.port = port
        else:
            raise TypeError("类型错误")

    def run(self) -> None:
        try:
            ret = os.system("{} {}".format(self.path, self.port))
            print(Back.BLUE, "{} 返回码 {}".format(self.name, ret), Style.RESET_ALL)
        except:
            print("服务端进程", Back.YELLOW + "{:16}".format(str(self.name)) + Style.RESET_ALL, "收到按键阻断事件")


class ClientProcess(Process):
    PYTHON_INTERPRETER = "python"
    def __init__(self, path, render=False, client="Demo", device="cpu", model="", 
                       lr=None, save_interval=None, log_interval=None):
        super(ClientProcess, self).__init__()
        if isinstance(path, str):
            self.path = path
            self.render = int(render)
            self.client = client
            self.device = device
            self.model = model
            self.lr = lr
            self.save_interval = save_interval
            self.log_interval = log_interval
        else:
            raise TypeError("类型错误")
    
    def run(self) -> None:
        try:
            if self.lr and self.save_interval and self.log_interval:
                ret = os.system("{} -u {} -c {} -d {} --model {} --lr {} --save_interval {} --log_interval {}".format(
                    self.PYTHON_INTERPRETER, 
                    self.path, 
                    self.client,
                    self.device,
                    self.model,
                    self.lr,
                    self.save_interval,
                    self.log_interval
                ))
            else:
                ret = os.system("{} -u {} -r {} -c {}".format(
                    self.PYTHON_INTERPRETER,
                    self.path,
                    self.render,
                    self.client
                ))
            print(Back.BLUE, "{} 返回码 {}".format(self.name, ret), Style.RESET_ALL)
        except KeyboardInterrupt:
            print("客户端进程", Back.YELLOW + "{:16}".format(str(self.name)) + Style.RESET_ALL, "收到按键阻断事件")

# 关闭进程
def close_all_process(process_group : List[Process]):
    for p in process_group:
        close_process(p)

def close_process(process : Process):
    if process.is_alive():
        process.terminate()
            
def check_process_group(process_group : List[Process]):
    for p in process_group:
        process_type = "客户端" if p.__class__.__name__ == "ClientProcess" else "服务端"
        if p.is_alive():
            print("{}进程  ".format(process_type), "{:18}".format(p.name), Back.RED + "尚未释放" + Style.RESET_ALL)
        else:
            print("{}进程  ".format(process_type), "{:18}".format(p.name), Back.GREEN + "已经释放" + Style.RESET_ALL)


if __name__ == "__main__":
    args = vars(parser.parse_args())

    # 使用LoadCoach函数检查输入的client是否在注册中
    for i in range(1, 5):
        _ = LoadCoach(args["agent{}".format(i)])

    with open("./launch/config.yaml", "r", encoding="utf-8") as fp:
        config = yaml.load(fp, Loader=yaml.Loader)

    # 打印训练配置表
    config_table = PrettyTable(field_names=["配置项", "值"])
    for k in config:
        if config[k]:
            val = ",".join(["{}号玩家".format(v + 1) for v in config[k]]) if k == "渲染列表" else config[k]
        else:
            val = "无"
        config_table.add_row([k, val])
    print(config_table)

    render_list = [False] * 4
    for pos in config["渲染列表"]:
        render_list[pos] = True

    # 训练智能体的游戏玩家/进程的配置参数
    trainee_args = dict(
        client       =args["agent1"],
        device       =args["device"],
        model        =args["model"],
        lr           =args["lr"],
        save_interval=args["save_interval"],
        log_interval =args["log_interval"]
    )

    MyProcessGroup : List[Process] = [
        ServeProcess(config["服务启动端路径"], config["游玩次数"]),
        ClientProcess(config["1号玩家"], render=render_list[0], **trainee_args),
        ClientProcess(config["2号玩家"], render=render_list[1], client=args["agent2"]),
        ClientProcess(config["3号玩家"], render=render_list[2], client=args["agent3"]),
        ClientProcess(config["4号玩家"], render=render_list[3], client=args["agent4"])
    ]

    for p in MyProcessGroup:
        p.start()
    try:
        for p in MyProcessGroup:
            if isinstance(p, ClientProcess):
                p.join()

    except BaseException as e:
        pass
    else:
        print(Back.BLUE, "所有游戏均已结束", Style.RESET_ALL)
    finally:
        os.system("taskkill /F /IM server.exe")
        # print(Back.CYAN + "正在处理余下的信息" + Style.RESET_ALL)
        close_all_process(MyProcessGroup)
        sleep(1)
        check_process_group(MyProcessGroup)