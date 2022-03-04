import numpy as np
import matplotlib.pyplot as plt
import os
from colorama import Back, Style

import matplotlib


try:
    plt.style.use("gadfly")
except:
    pass
def DrawCheckpoints(checkpoint, root_dir=r".\model"):
    checkpoint_path = os.path.join(root_dir, checkpoint)
    for file in os.listdir(checkpoint_path):
        if file == "value.log":
            log_path = os.path.join(checkpoint_path, file)
            break
    else:
        print(Back.RED, "警告: 未发现value.log文件, 请检查checkpoint是否损坏", Style.RESET_ALL)
        exit(-1)
    
    data_line = False
    values = []
    counts = []
    losses = []
    rewards = []
    episodes = []
    label_fontsize = 16
    for line in open(log_path, "r", encoding="utf-8"):
        line = line.strip()

        if data_line:
            if mode == "Imitation":
                value = line.split()[-1]
                if value == "nan":
                    break
                else:
                    value = float(value)
                count = line.split()[0].split("=")[-1][:-1]
                count = int(count)
                values.append(value)
                counts.append(count)
            elif mode == "Reinforcement":
                spts = line.split()
                loss = float(spts[3])
                reward = float(spts[-1])
                episode = int(spts[0].split('=')[-1][:-1])
                losses.append(loss)
                rewards.append(reward)
                episodes.append(episode)
        
        if line.startswith("* MODE"):
            mode = line.split()[-2]
            if mode in ["Imitation", "Reinforcement"]:
                data_line = True
            else:
                print(Back.RED, "警告: 无法识别MODE :", mode, Style.RESET_ALL)
                exit(-1)

    if mode == "Imitation":
        plt.plot(counts, values, '--o')
        plt.ylabel("value", fontsize=label_fontsize)
        plt.xlabel("count", fontsize=label_fontsize)
        plt.title("imitation learning")
    elif mode == "Reinforcement":
        losses = np.array(losses)
        rewards = np.array(rewards)
        # losses = losses / max(losses)
        rewards = (rewards - rewards.min()) / np.ptp(rewards) * 60000
        plt.plot(episodes, losses, '--o', label="loss")
        plt.plot(episodes, rewards, '--o', label="reward")
        plt.ylabel(r"$loss(\times1)/reward(\times60000)$", fontsize=label_fontsize)
        plt.xlabel("episode", fontsize=label_fontsize)
        plt.title("reinforcement learning")
    

DrawCheckpoints("checkpoints_2022_3_3_22_40_23")
plt.legend()
plt.tight_layout()
plt.show()