先启动服务端，再启动客户端

启动服务端:(Windows)
```bash
> windows\server.exe <端口号>
```

启动客户端:分别在四个独立进程的命令行中运行:
```bash
> python -u clients\client1.py
> python -u clients\client2.py
> python -u clients\client3.py
> python -u clients\client4.py
```

---
每个客户端程序需要处理服务端发过来的message，并返回动作列表中的索引以完成一次出牌。

也就是说，我们的agent的输入是一个字典message，返回值是一个整数，代表动作序号。

在某一次发牌后，我们运行如下程序打印message中的信息:
```python
for k in message:
    print(k, message[k])
```
得到的信息如下:
```python
type act
stage play
handCards ['C4', 'S5', 'H5', 'C5', 'H6', 'D6', 'S7', 'S8', 'D8', 'S9', 'C9', 'D9', 'ST', 'DT', 'SJ', 'HJ', 'HJ', 'CJ', 'SQ', 'HQ', 'CQ', 'SK', 'DK', 'HA', 'S2', 'S2', 'C2']
publicInfo [
    {'rest': 27, 'playArea': None}, 
    {'rest': 27, 'playArea': None}, 
    {'rest': 22, 'playArea': ['Straight', '6', ['S6', 'H7', 'H2', 'H2', 'CT']]}, 
    {'rest': 22, 'playArea': ['Straight', '9', ['H9', 'HT', 'DJ', 'DQ', 'DK']]}
]
selfRank 2
oppoRank 2
curRank 2
curPos 3
curAction ['Straight', '9', ['H9', 'HT', 'DJ', 'DQ', 'DK']]
greaterPos 3
greaterAction ['Straight', '9', ['H9', 'HT', 'DJ', 'DQ', 'DK']]
actionList [['PASS', 'PASS', 'PASS'], ['Straight', 'T', ['ST', 'SJ', 'SQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'SJ', 'SQ', 'DK', 'HA']], ['Straight', 'T', ['ST', 'SJ', 'HQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'SJ', 'HQ', 'DK', 'HA']], ['Straight', 'T', ['ST', 'SJ', 'CQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'SJ', 'CQ', 'DK', 'HA']], ['Straight', 'T', ['ST', 'HJ', 'SQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'HJ', 'SQ', 'DK', 'HA']], ['Straight', 'T', ['ST', 'HJ', 'HQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'HJ', 'HQ', 'DK', 'HA']], ['Straight', 'T', ['ST', 'HJ', 'CQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'HJ', 'CQ', 'DK', 'HA']], ['Straight', 'T', ['ST', 'CJ', 'SQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'CJ', 'SQ', 'DK', 'HA']], ['Straight', 'T', ['ST', 'CJ', 'HQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'CJ', 'HQ', 'DK', 'HA']], ['Straight', 'T', ['ST', 'CJ', 'CQ', 'SK', 'HA']], ['Straight', 'T', ['ST', 'CJ', 'CQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'SJ', 'SQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'SJ', 'SQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'SJ', 'HQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'SJ', 'HQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'SJ', 'CQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'SJ', 'CQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'HJ', 'SQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'HJ', 'SQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'HJ', 'HQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'HJ', 'HQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'HJ', 'CQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'HJ', 'CQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'CJ', 'SQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'CJ', 'SQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'CJ', 'HQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'CJ', 'HQ', 'DK', 'HA']], ['Straight', 'T', ['DT', 'CJ', 'CQ', 'SK', 'HA']], ['Straight', 'T', ['DT', 'CJ', 'CQ', 'DK', 'HA']], ['Bomb', 'J', ['SJ', 'HJ', 'HJ', 'CJ']], ['StraightFlush', '7', ['S7', 'S8', 'S9', 'ST', 'SJ']], ['StraightFlush', '8', ['S8', 'S9', 'ST', 'SJ', 'SQ']], ['StraightFlush', '9', ['S9', 'ST', 'SJ', 'SQ', 'SK']]]
indexRange 40
```

每张牌由花色+点数组成，所以是一个含有两个字母的字符串，具体含义见file:///E:/Project/NUAA-guandan/doc/掼蛋软件2010资料包/掼蛋平台使用说明书1006.pdf

最终的返回值必须在0-39之间。

其中0代表什么都不出。