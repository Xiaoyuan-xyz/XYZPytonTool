import numpy as np

# 假设双方分别为A B 左右手分别为L R
# 当前一个状态可以用 (al, ar, bl, br) 表示

N = 10


def sort_state(l, r):
    # 永远让右手大于等于左手
    return (l, r) if l <= r else (r, l)


def state_norepeat(states):
    # 给定一个state的列表 去重
    new_states = []
    for sta in states:
        if sta not in new_states:
            new_states.append(sta)
    return new_states


def possible_action(state_tuble):
    """
    给定状态 返回之后的状态
    这里是指a行动一次后的结果
    """
    al, ar, bl, br = state_tuble
    raw_actions = []
    if al != 0:
        if bl != 0:
            nall = (al + bl) % N
            raw_actions.append((*sort_state(nall, ar), bl, br))
        if br != 0:
            nalr = (al + br) % N
            raw_actions.append((*sort_state(nalr, ar), bl, br))
    if ar != 0:
        if bl != 0:
            narl = (ar + bl) % N
            raw_actions.append((*sort_state(narl, al), bl, br))
        if br != 0:
            narr = (ar + br) % N
            raw_actions.append((*sort_state(narr, al), bl, br))

    return state_norepeat(raw_actions)


def possible_before(state_tuble):
    """
    给定一个局面 返回之前的状态
    这里是指a如何可以到达这个局面
    """
    al, ar, bl, br = state_tuble
    possible = []
    if ar == 0:  # 我方全0
        if bl != 0:
            possible.append((0, N - bl, bl, br))
        if br != 0:
            possible.append((0, N - br, bl, br))
    elif al == 0:  # 我方有一个0
        if bl != 0:
            possible.append((*sort_state(N - bl, ar), bl, br))
            if ar != bl:
                possible.append((*sort_state(0, (ar - bl) % N), bl, br))
        if br != 0:
            possible.append((*sort_state(N - br, ar), bl, br))
            if ar != br:
                possible.append((*sort_state(0, (ar - br) % N), bl, br))
    else:  # 我方全不为0
        if bl != 0:
            if al != bl:
                possible.append((*sort_state((al - bl) % N, ar), bl, br))
            if ar != bl:
                possible.append((*sort_state(al, (ar - bl) % N), bl, br))
        if br != 0:
            if al != br:
                possible.append((*sort_state((al - br) % N, ar), bl, br))
            if ar != br:
                possible.append((*sort_state(al, (ar - br) % N), bl, br))
    return state_norepeat(possible)


def change_position(state_tuble):
    """
    交换两人状态
    """
    al, ar, bl, br = state_tuble
    return (bl, br, al, ar)


def possible_action_rival(state_tuble):
    """
    b行动后的状态
    """
    return [change_position(it) for it in possible_action(change_position(state_tuble))]


def possible_before_rival(state_tuble):
    """
    b行动前的状态
    """
    return [change_position(it) for it in possible_before(change_position(state_tuble))]


# 接下来我们考虑一个矩阵score
# 这个矩阵是100*100的 换句话说每一种状态都对应其中一个元素
# 然而我们之前要求左手小于等于右手
# 所以我们把左手大于右手的情况记在对称的位置
# 这就要求提供一个转换方式

def index(state_tuble):
    """
    返回在score矩阵中的位置
    """
    al, ar, bl, br = state_tuble
    return (al * N + ar, bl * N + br)


def getv(score, state):
    return score[*index(state)]


def setv(score, state, value):
    score[*index(state)] = value


def main():
    M = 25
    score = np.ones((N * N, N * N), dtype='int') * M

    # score中存放的值应该这样被解读
    # score[state] 表示轮到b时 a获胜的回合数
    # 这里M是一个很大的值
    # 0表示a取胜 2M表示b取胜

    # 那么如何计算score中的值呢？
    # 从已知的出发
    # 先把游戏结束结束时的场面记下来

    state_queue = []
    for bl in range(N):
        for br in range(N):
            if br == 0 and bl == 0:
                continue
            if bl <= br:
                # 其实这里的b获胜的场合并不符合score的定义
                # 因为在实际游戏中并不会得到轮到对手行动 但对手却全是0的场合
                # 但这里它们只是为了标记胜利而已
                # 这样的话实际b胜利的情形 比如(1, 2, 0, 8) 会被记为199
                state = (0, 0, bl, br)
                state_queue.append(state)
                state_queue.append(change_position(state))
                setv(score, state, 0)
                setv(score, change_position(state), 2 * M)
    score[0, 0] = -1

    n_state = len(state_queue)

    # 接下来就是遍历每一种状态

    count = 0
    while len(state_queue) > 0:
        count += 1
        if count == 100000:
            print('达到最大遍历次数 退出循环')
            break
        state = state_queue.pop(0)
        old_value = getv(score, state)

        # 考察一个状态 实际上是根据现有的score去重新计算
        # 是一个最大最小优化
        # 考察对手的所有可能的行动
        # 在每个对手的行动中 他会最大化自己的得分
        rival_view = change_position(state)
        rival_action = possible_action(rival_view)
        if len(rival_action) > 0:
            values = [getv(score, it) for it in rival_action]
            # values是站在b视角看自己能否胜利
            # 在所有选择中 找出最小的那个值 这就是b对自己胜利的期望回合数
            # 同时对应的选择也就是b会走的方向
            v = min(values)

            if v < M:
                # 而a则要比那多一个回合
                # 例如如果b认为自己会在3回合后获胜
                # 那么a会给自己打分196
                setv(score, state, 2 * M - 1 - v)
            elif v > M:
                # 反之 如果b认为自己197的话
                # a会认为自己4回合后获胜
                setv(score, state, 2 * M + 1 - v)

        # 注意这里 前108个即使score没有变也要通知更新
        if getv(score, state) == old_value and count > n_state:
            continue

        # 当这个值变动后 需要通知更新它的全体上游
        # 它的上游是b的回合 所以我们干脆把它倒过来加进queue中
        need_updates = possible_before(state)
        for it in need_updates:
            cp_it = change_position(it)
            if cp_it in state_queue:
                continue
            state_queue.append(cp_it)

    return score


def search(score, state):
    M = 25
    """
    给定当前状态 自动判断胜负
    """
    v = getv(score, state)
    print(v)
    if v < M:
        print('对手先 你获胜')
    elif v > M:
        print('对手先 你输')
    else:
        print('对手先 平局')
    print('')
    acts = possible_action_rival(state)
    ret = []
    for act in acts:
        ret.append(getv(score, change_position(act)))
        print(change_position(act), getv(score, change_position(act)))
    return acts, ret


if __name__ == '__main__':
    score = main()
    ssss = (1, 1, 1, 1)
    while True:
        acts, _ = search(score, ssss)
        i = input('请输入选择的序号')
        act = acts[int(i)]

        ssss = change_position(act)
        acts, ret = search(score, ssss)
        choo = np.argmin(ret)
        print('电脑选择了', acts[choo])
        ssss = change_position(acts[choo])

# TODO: 有了这段程序可以保证必不败了 但如何抓住对方的失误？
