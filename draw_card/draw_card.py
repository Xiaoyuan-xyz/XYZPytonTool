# 这是一个模拟抽卡

import numpy as np
from matplotlib import pyplot as plt
import random
from tqdm import tqdm

random.seed(42)
prob = np.zeros([99])
prob[:51] = 0.98 ** np.arange(51)
for i in range(50, 99):
    prob[i] = prob[i-1] * (1.0 - 0.02 * (i - 49))

def next_six_star(k=1):
    return random.choices(np.arange(99, 0, -1), cum_weights=prob[::-1], k=k)


if __name__ == '__main__':
    epoch = 0
    ret = {}
    for i in tqdm(range(10000000)):
        draw = 0
        result = [0, 0, 0]
        while True:
            draw += next_six_star()[0]
            if draw > 300:
                break
            # 限定0 陪跑1 歪2
            which = random.choices([0, 1, 2], weights=[0.35, 0.35, 0.3], k=1)[0]
            result[which] += 1
        if tuple(result) in ret:
            ret[tuple(result)] += 1
        else:
            ret[tuple(result)] = 1
        epoch += 1
    print(ret)

