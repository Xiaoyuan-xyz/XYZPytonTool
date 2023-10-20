import re
from collections import Counter

import numpy as np


def read_index_file(path):
    data = np.loadtxt(path, dtype=int)
    return data


def tenhou_to_vector(mahjong):
    """
    天风格式转34长向量
    """
    counts_array = np.zeros(34, dtype=int)

    mahjong = mahjong.replace('0', '5')

    manzu_pattern = r'\d+m'
    manzu = re.search(manzu_pattern, mahjong)
    if manzu:
        manzu = manzu.group()[:-1]
        manzu_counts = Counter(manzu)
        for digit, count in manzu_counts.items():
            if int(digit) == 0:
                counts_array[4] += count
                continue
            counts_array[int(digit) - 1] += count

    pinzu_pattern = r'\d+p'
    pinzu = re.search(pinzu_pattern, mahjong)
    if pinzu:
        pinzu = pinzu.group()[:-1]
        pinzu_counts = Counter(pinzu)
        for digit, count in pinzu_counts.items():
            if int(digit) == 0:
                counts_array[13] += count
                continue
            counts_array[int(digit) + 8] += count

    souzu_pattern = r'\d+s'
    souzu = re.search(souzu_pattern, mahjong)
    if souzu:
        souzu = souzu.group()[:-1]
        souzu_counts = Counter(souzu)
        for digit, count in souzu_counts.items():
            if int(digit) == 0:
                counts_array[22] += count
                continue
            counts_array[int(digit) + 17] += count

    jihai_pattern = r'[1-7]+z'
    jihai = re.search(jihai_pattern, mahjong)
    if jihai:
        jihai = jihai.group()[:-1]
        jihai_counts = Counter(jihai)
        for digit, count in jihai_counts.items():
            counts_array[int(digit) + 26] += count
    return counts_array


def shanten_kokushi(vec):
    """
    国士计算向听数
    """
    yaotyuu = np.array([0, 8, 9, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33])
    kind = np.sum(vec[yaotyuu] > 0)
    pair = np.any(vec[yaotyuu] > 1)
    result = 13 - kind - (1 if pair else 0) - 1
    return result


def shanten_chiitoi(vec):
    """
    七对计算向听数
    """
    pair = np.sum(vec > 1)
    result = 6 - pair
    return result


def base5_to_index(pai_array):
    decimal_result = int("".join(map(str, pai_array)), 5)
    return decimal_result


suupai_index = read_index_file('index_s.txt')
jihai_index = read_index_file('index_h.txt')

pai_name = ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m', '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
            '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', '东', '南', '西', '北', '白', '发', '中']


def shanten_ippan(vec):
    """
    一般形（四面子+一雀头）计算
    """
    manzu = suupai_index[base5_to_index(vec[:9])]
    pinzu = suupai_index[base5_to_index(vec[9:18])]
    souzu = suupai_index[base5_to_index(vec[18:27])]
    jihai = jihai_index[base5_to_index(vec[27:])]

    d = np.zeros(shape=(4, 5), dtype=int)
    b = np.zeros(shape=(4, 5), dtype=int)
    d[0] = manzu[:5]
    d[1] = pinzu[:5]
    d[2] = souzu[:5]
    d[3] = jihai[:5]
    b[0] = manzu[5:]
    b[1] = pinzu[5:]
    b[2] = souzu[5:]
    b[3] = jihai[5:]

    dd = np.zeros(shape=(4, 5), dtype=int)
    bb = np.zeros(shape=(4, 5), dtype=int)
    dd[0] = d[0]
    bb[0] = b[0]

    for x in range(3):  # 花色遍历 下标从0开始所以-1
        for n in range(5):  # 上标 面子数遍历
            temp = 100
            for k in range(n + 1):
                now = dd[x, k] + d[x + 1, n - k]
                if now < temp:
                    temp = now
            dd[x + 1, n] = temp

            temp = 100
            for k in range(n + 1):
                now = min(bb[x, k] + d[x + 1, n - k], dd[x, k] + b[x + 1, n - k])
                if now < temp:
                    temp = now
            bb[x + 1, n] = temp

    return bb[3, sum(vec)//3] - 1


def calc_shanten(mahjong):
    if type(mahjong) == str:
        vec = tenhou_to_vector(mahjong)
    else:
        vec = mahjong
    return min(shanten_kokushi(vec), shanten_ippan(vec), shanten_chiitoi(vec))


def clac_youkouhai(vec):
    """
    切一张之后 计算哪张是进张 返回总进张数
    """
    shanten = calc_shanten(vec)
    total_yuukouhai = 0
    yuukouhai = []
    yuukouhai_index = []
    for i in range(34):
        if vec[i] < 4:
            new_vec = vec.copy()
            new_vec[i] += 1
            if calc_shanten(new_vec) == shanten - 1:
                yuukouhai.append(pai_name[i])
                total_yuukouhai += 4 - vec[i]
                yuukouhai_index.append(i)
    return total_yuukouhai, yuukouhai, shanten, yuukouhai_index

def calc_13(mahjong):
    if type(mahjong) == str:
        vec = tenhou_to_vector(mahjong)
    else:
        vec = mahjong
    assert sum(vec) == 13

    total_yuukouhai, yuukouhai, shanten, _ = clac_youkouhai(vec)
    print(f'当前向听数：{shanten} 有效牌张数：{total_yuukouhai} {yuukouhai}')
    return yuukouhai


def calc_tenpai(mahjong):
    """
    切哪张听牌
    """
    if type(mahjong) == str:
        vec = tenhou_to_vector(mahjong)
    else:
        vec = mahjong
    shanten = calc_shanten(vec)
    assert sum(vec) == 14
    if shanten != 0:
        return

    max_yuukouhai = 0
    for i in range(34):
        if vec[i] > 0:
            new_vec = vec.copy()
            new_vec[i] -= 1
            if calc_shanten(new_vec) == shanten:
                total_yuukouhai, yuukouhai, _, _ = clac_youkouhai(new_vec)
                print(f'     切{pai_name[i]} 有效牌张数：{total_yuukouhai} {yuukouhai}')
                if total_yuukouhai > max_yuukouhai:
                    max_yuukouhai = total_yuukouhai
    return max_yuukouhai


def calc_1shanten(mahjong):
    """
    切哪张进入一向听
    """
    vec = tenhou_to_vector(mahjong)
    shanten = calc_shanten(vec)
    assert shanten == 1
    assert sum(vec) == 14

    max_yuukouhai = 0
    for i in range(34):
        if vec[i] > 0:
            new_vec = vec.copy()
            new_vec[i] -= 1
            if calc_shanten(new_vec) == shanten:
                print(f'切{pai_name[i]}进入一向听')
                # 切掉一张进入一向听
                total_yuukouhai, _, _, yuukouhai_index = clac_youkouhai(new_vec)
                total_score = 0 # 听牌机会
                for i in yuukouhai_index:
                    new_new_vec = new_vec.copy()
                    new_new_vec[i] += 1
                    score = calc_tenpai(new_new_vec)
                    print(f'{pai_name[i]}:{score}', end='== \n')
                    total_score += (4 - new_vec[i]) * score
                avg_score = total_score / total_yuukouhai
                print(f'\n总进张{total_yuukouhai}*听牌时平均张数{avg_score:.2f}={total_score}')



if __name__ == '__main__':
    mahjong = '23499m06789p'
    s = calc_shanten(mahjong)
    if s == 0:
        print('听牌')
        print(calc_tenpai(mahjong))
    elif s == 1:
        print('一向听')
        print(calc_1shanten(mahjong))
