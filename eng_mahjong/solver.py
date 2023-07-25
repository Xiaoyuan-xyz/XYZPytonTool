import string
import time

import numpy as np
import pulp

from word_list import count_letter

pulp.LpSolverDefault.msg = 0

status = ['LpStatusNotSolved', 'LpStatusOptimal', 'LpStatusUndefined', 'LpStatusUnbounded', 'LpStatusInfeasible']

raw_path = './raw/'
cleanup_path = './cleanup/'
wordlist_path = './wordlist/'
levels = ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']
ae_names = ['ae_a1.txt', 'ae_a2.txt', 'ae_b1.txt', 'ae_b2.txt', 'ae_c1.txt', 'ae_c2.txt']
be_names = ['be_a1.txt', 'be_a2.txt', 'be_b1.txt', 'be_b2.txt', 'be_c1.txt', 'be_c2.txt']


def solver(data, mahjong):
    len_dic = data.shape[1]
    problem = pulp.LpProblem("mahjong_solver", pulp.LpMinimize)
    xs = [pulp.LpVariable(f"x{i}", lowBound=0, cat='Integer') for i in range(len_dic)]
    ones = np.ones((len_dic,))
    problem += pulp.lpDot(ones, xs)  # 词的数量越少越好
    for i in range(26):
        problem += (pulp.lpDot(data[i], xs) == mahjong[i])

    problem.solve()
    s = np.array([x.value() for x in xs], dtype='int32')
    # print(status[problem.status])
    nonzero_indexes = np.nonzero(s)[0]
    return problem.status, nonzero_indexes, s[nonzero_indexes]


def display_result(word_list, indexes, count):
    ret = []
    for i, c in zip(indexes, count):
        ret.extend([word_list[i] * c])
    return ret


def tingpai_check(mahjong, word_list, debug=True):
    data = count_letter(word_list)
    tingpai = []
    for letter in string.ascii_lowercase:
        need_check = mahjong + letter
        need_check = count_letter([need_check]).squeeze()

        status, indexes, counts = solver(data, need_check)
        if debug:
            if status == 1:
                print(f'{letter}和牌', ' '.join(display_result(word_list, indexes, counts)))
            else:
                print(f'{letter}无法和牌')
        if status == 1:
            tingpai.append(letter)
    return tingpai


if __name__ == '__main__':
    with open(wordlist_path + f'mix_{levels[5]}.txt', 'r', encoding='utf8') as file:
        word_list = [line.strip() for line in file]
    with open(wordlist_path + 'oxford.txt', 'r', encoding='utf8') as file:
        word_list = [line.strip() for line in file]
    data = count_letter(word_list)

    while True:
        mahjong_str = input('请输入字符串')
        mahjong = count_letter([mahjong_str]).squeeze()

        start_time = time.time()
        problem_status, indexes, counts = solver(data, mahjong)
        print(f'花费时间{time.time() - start_time:4f}s')
        print(status[problem_status])
        if problem_status == 1:
            print(display_result(word_list, indexes, counts))
        else:
            max_tingpai = None
            max_i = -1
            max_tingpai_num = 0
            for i in range(len(mahjong_str)):
                new_mahjong = mahjong_str[:i] + mahjong_str[i + 1:]
                tingpai = tingpai_check(new_mahjong, word_list)
                print(mahjong_str[i], len(tingpai), tingpai)
                if max_tingpai_num < len(tingpai):
                    max_tingpai_num = len(tingpai)
                    max_i = i
                    max_tingpai = tingpai
            print(f'一向听 最大听牌切{mahjong_str[max_i]}听{max_tingpai_num}张 {max_tingpai}')

# mueuueozeroqtc
# 切z听['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'v', 'w', 'y']
# 切q什么都听不了
