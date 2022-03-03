# NUAA 2021 基于深度学习的掼蛋系统
- [x] 模仿学习测试
- [ ] 强化学习测试
- [ ] 完成参数`agent1`的实现（难点：不同的coach代码实现形式不统一，需要进行整合，提示：整合所有的parse函数）
- [ ] 支持Linux（修改服务启动路径、修改launch.py干掉剩余进程的指令，改成kill）

项目结构：
```
|- dist: 最终得到的模型的部署目录

|- doc: 参考文件

|- src: 源代码

|- clients : 启动游戏玩家的客户端，这是游戏中度量玩家的最小单元

|- launch : 启动游戏的地方，你需要通过这个文件夹中的工具快速开启服务，这是整个项目的中枢。

|- coach : 曾经最强的几支队伍的代码。已经在coach模块中进行注册和整合。

|- test: 测试目录

|- |-> platform: 存放模拟器的目录

|- |-> analysis: 分析数据的代码

|- |-> test_space: 测试空间

|- |-> unit_test: 模块单元测试
```

---
# 启动说明

## 快速开始
我们来尝试开启一个非训练模式的游戏，请先打开`./launch/config.yaml`, 修改如下:

```yaml
# 都是中文变量，不需要我解释了吧=_=
1号玩家: .\clients\client1.py
2号玩家: .\clients\client2.py
3号玩家: .\clients\client3.py
4号玩家: .\clients\client4.py
服务启动端路径: .\simulator\windows\server.exe
渲染列表: []
游玩次数: 5  # 玩五次应该很快会结束
```


> 整个系统，无论是训练还是推理，都是通过`launch/launch.py`文件来执行的，但是`launch.py`需要配置的参数比较多。为了方便使用，我还对`launch.py`进行了二次封装，比如`train.py`。

## 获取说明
通过配置**launch.py的参数和config.yaml文件**，我们便可以让系统执行训练或者推理的行为，具体的参数说明我都写在`add_argument`函数中了，执行如下语句来获取帮助：

```bash
python -u launch/launch.py -h
```

---

# 训练说明

## 生成模型路径
为了封装完整，模块化（~~为了摸鱼~~）。如果你需要训练模型，请不要修改`launch/config.yaml`文件，请直接使用`train.py`，且整个模型默认只训练第一个agent。

训练产生的checkpoints默认会创建在`./model/checkpoints_年_月_日_时_分_秒`文件夹中。产生的每个pth结构如下：
```json
{
    "coach" : COACH,   // 模仿学习初始化的 coach 模型
    "model_state_dict" : self.ValueNet.state_dict(),   // Q网络的state_dict
    "model_class"  : ActionValueNet   // 使用的神经网络的前馈类
}
```

## 断点续训

`train.py`可以接受一个参数`model`，默认是`None`，即从头训练。如果你需要进行断点续训，请指派该参数，参数的内容为数据结构和上述描述的pth一致的（至少包含`model_state_dict`），如果输入的pickle同时包含`model_state_dict`与`model_class`，请确保它们保持一致。

---

# 测试

如果你像修改或添加`coach`中的代码，我强烈建议使用`unit_test/test_coach.py`进行验证。如果运行完该文件并没有报错，则说明编写的coach程序没有问题。同理，如果你需要修改我的多进程，在修改完后也请运行测试用例。