import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from game1111 import main, possible_action, getv, change_position


def print_heatmap(mat):
    plt.imshow(mat)
    plt.colorbar()
    plt.show()


def print_fullmap(score):
    plt.figure(figsize=(30, 30))
    plt.imshow(score)
    plt.colorbar()
    plt.xticks(indexes)
    plt.yticks(indexes)
    plt.show()


# 下面我们关心从(1, 1, 1, 1)状态开始的演变
# 如果有多个可行解 则均分概率 最后看看都集中在哪里

def my_turn(score, state):
    actions = possible_action(state)  # 留给对手的局面
    values = [getv(score, it) for it in actions]  # 自己的分数
    if len(values) == 0:
        return [], []
    values = np.array(values)
    m = np.min(values)
    i = values == m
    values = list(values[i])
    actions = [tuple(it) for it in list(np.array(actions)[i])]
    return actions, values


def rival_turn(score, state):
    # 返回的是b的最优解和a的打分
    rival = change_position(state)
    actions, values = my_turn(score, rival)
    return [change_position(it) for it in actions], [2 * M - it for it in values]


def my_turn_all(score, state):
    actions = possible_action(state)  # 留给对手的局面
    values = [getv(score, it) for it in actions]  # 自己的分数
    return actions, values


def rival_turn_all(score, state):
    # 返回的是b的最优解和a的打分
    rival = change_position(state)
    actions, values = my_turn_all(score, rival)
    return [change_position(it) for it in actions], [2 * M - it for it in values]


def evolution(score, funcs=None):
    heat = np.zeros((55, 55))
    heat[10, 10] = 1  # (1, 1, 1, 1)
    reachable = np.zeros((100, 100))

    if funcs == None:
        funcs = [rival_turn, my_turn]

    for iter_index in tqdm(range(41)):
        # plt.imshow(heat)
        # plt.colorbar()
        # plt.savefig(f'./heatmap/{iter_index}.png')
        # plt.close()

        for iter_func_index in range(2):
            new_heat = np.zeros((100, 100))
            for it_i in range(55):
                i = indexes[it_i]
                my_state = (i // N, i % N)
                for it_j in range(55):
                    j = indexes[it_j]
                    rival_state = (j // N, j % N)
                    if heat[it_i, it_j] == 0:
                        continue
                    acts, vm = funcs[iter_func_index](score, (*my_state, *rival_state))
                    n_act = len(acts)
                    if n_act > 0:
                        piece = heat[it_i, it_j] / n_act
                        for act in acts:
                            al, ar, bl, br = act
                            ii = al * N + ar
                            jj = bl * N + br
                            new_heat[ii, jj] += piece
                            reachable[ii, jj] = 1
                    else:
                        new_heat[i, j] = heat[it_i, it_j]
            heat = new_heat[indexes, :][:, indexes]
    return heat, reachable


score = main()
M = 25
N = 10
mat = score.copy()
indexes = []  # score中实际有意义的值
for l in range(N):
    for r in range(N):
        if l <= r:
            indexes.append(l * N + r)
mat = mat[indexes, :][:, indexes]

heat, reachable_clever = evolution(score)
_, reachable = evolution(score, [rival_turn_all, my_turn_all])
unclever = reachable - reachable_clever
unclever[:10, :] = 0
unclever[:, :10] = 0
plt.imshow(unclever)
plt.show()

print(np.stack(np.nonzero(unclever)).T)

'''
[[11 69]
 [11 79]
 [11 99]
 [13 79]
 [13 99]
 [14 69]
 [14 99]
 [16 44]
 [16 49]
 [17 33]
 [17 39]
 [19 19]
 [22 38]
 [23 77]
 [23 78]
 [25 58]
 [27 38]
 [27 88]
 [33 17]
 [33 77]
 [33 78]
 [37 37]
 [38 22]
 [38 27]
 [39 17]
 [39 77]
 [44 16]
 [45 56]
 [49 16]
 [49 66]
 [56 45]
 [58 25]
 [66 49]
 [69 11]
 [69 14]
 [77 23]
 [77 33]
 [77 39]
 [78 23]
 [78 33]
 [79 11]
 [79 13]
 [88 27]
 [99 11]
 [99 13]
 [99 14]]
'''
