import numpy as np
import tqdm
from matplotlib import pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

prob = [0.27, 0.265, 0, 36.225/165]
prob[2] = 1 - sum(prob)
pt = [90, 45, 0, -165]

def plot_cdf(data, label=''):
    hist, bins = np.histogram(data, bins=10000, density=False)
    pdf = hist / sum(hist)
    cdf = np.cumsum(pdf)
    plt.plot(bins[:-1], cdf, label=label)

def game_play(times):
    # 以prob为概率，随机生成times个1-4的随机数
    return np.average(np.random.choice(pt, times, p=prob))

n = 200000
test_times = [1000]

for times in test_times:
    data = np.zeros(n)
    for i in tqdm.tqdm(range(n)):
        data[i] = game_play(times)
    plot_cdf(data, label=f'{times}')

plt.legend()
plt.xlabel('平均得点')
plt.ylabel('累计概率分布')
plt.xlim(-10, 10)
plt.yticks(np.arange(0, 1.05, 0.05))
plt.grid()
plt.show()