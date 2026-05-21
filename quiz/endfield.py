import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# 概率
P_BASE = [0.60, 0.24, 0.109, 0.05, 0.027]
P_SKILL = [0.109, 0.042]

TARGET_PATH = [
    (1, 1, 1),
    (2, 2, 1),
    (3, 3, 1),
    (4, 4, 1),
    (4, 4, 2),
    (5, 5, 2),
    (5, 5, 3),
    (6, 6, 3),
]

N_STAGE = len(TARGET_PATH)


def attempt_upgrade(level, prob_table):
    if level >= len(prob_table) + 1:
        return level
    if np.random.rand() < prob_table[level - 1]:
        return level + 1
    return level


def simulate_one_run(n_items):
    base, add, skill = 1, 1, 1
    stage = 0

    stage_record = np.zeros(n_items, dtype=int)

    for i in range(n_items):

        if stage < N_STAGE:
            target = TARGET_PATH[stage]

            if base < target[0]:
                base = attempt_upgrade(base, P_BASE)
            elif add < target[1]:
                add = attempt_upgrade(add, P_BASE)
            elif skill < target[2]:
                skill = attempt_upgrade(skill, P_SKILL)

            if (base, add, skill) == target:
                stage += 1

        stage_record[i] = stage

    return stage_record


def monte_carlo_stage_distribution(n_items, n_sim):
    # 统计数组
    # shape = (n_items, N_STAGE+1)
    dist = np.zeros((n_items, N_STAGE + 1))

    for _ in tqdm(range(n_sim)):
        stages = simulate_one_run(n_items)
        for i in range(n_items):
            dist[i, stages[i]] += 1

    dist /= n_sim
    return dist


# ==============================
# 运行模拟
# ==============================

n_items = 300
n_sim = 20000

dist = monte_carlo_stage_distribution(n_items, n_sim)


# ==============================
# 画图
# ==============================

x = np.arange(1, n_items + 1)

plt.figure(figsize=(10, 6))

for s in range(N_STAGE):
    plt.plot(x, dist[:, s+1], label=f"{TARGET_PATH[s]}")

plt.xlabel("Number of items used")
plt.ylabel("Probability")
plt.title("Stage Distribution vs Number of Items")
plt.legend()
plt.grid(True)

plt.show()
