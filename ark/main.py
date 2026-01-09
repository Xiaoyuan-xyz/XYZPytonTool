# 这是一个明日方舟抽卡统计模拟器
# 我觉得为了获知卡池的某些数据 还应该统计更多数值

import numpy as np
from tqdm import tqdm
from matplotlib import pyplot as plt

n = 100000

def simulate_vectorized(n):
    ret = {}
    for _ in tqdm(range(n)):
        up1 = 0
        up2 = 0
        up3 = 0
        now_prob = 0.02
        no_six = 0
        for _ in range(600):
            rand = np.random.random()
            if rand < now_prob:
                rand = np.random.random()
                if rand < 0.35:
                    up1 += 1
                elif rand < 0.7:
                    up2 += 1
                else:
                    up3 += 1
                now_prob = 0.02
                no_six = 0
            else:
                no_six += 1
                if no_six >= 50:
                    now_prob += 0.02
        ret[up1] = ret.get((up1), 0) + 1
    return ret

# 向量化操作
ret = simulate_vectorized(n)

probabilities = {k: v / n for k, v in ret.items()}

# 提取x和y值
x = list(probabilities.keys())
y = list(probabilities.values())

# 绘制柱状图
plt.bar(x, y, color='skyblue')
plt.xlabel('Value')
plt.ylabel('Probability')
plt.title('Probability Distribution')
plt.xticks(range(min(x), max(x) + 1))
plt.show()

print(ret[0] / n)