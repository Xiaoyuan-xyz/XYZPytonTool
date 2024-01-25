from shanten import calc_shanten
from shanten import tenhou_to_vector, calc_ukeire

if __name__ == '__main__':

    nss = [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 2],
        [1, 1, 1, 1, 2, 1],
        [1, 1, 1, 2, 1, 1],
        [1, 1, 1, 1, 3],
        [1, 1, 1, 3, 1],
        [1, 1, 3, 1, 1],
        [1, 1, 1, 4],
        [1, 1, 4, 1],
        [1, 1, 1, 2, 2],
        [1, 1, 2, 1, 2],
        [1, 2, 1, 1, 2],
        [2, 1, 1, 1, 2],
        [1, 1, 2, 2, 1],
        [1, 2, 1, 2, 1],
        [1, 1, 2, 3],
        [1, 1, 3, 2],
        [1, 2, 1, 3],
        [1, 3, 1, 2],
        [2, 1, 1, 3],
        [1, 2, 3, 1],
        [1, 2, 4],
        [1, 4, 2],
        [2, 1, 4],
        [1, 3, 3],
        [3, 1, 3],
        [3, 4],
        [1, 2, 2, 2],
        [2, 1, 2, 2],
        [2, 2, 3],
        [2, 3, 2],
    ]

    kind27 = []
    nums = []
    for ns in nss:
        pai = len(ns)

        n_distance = pai - 1
        max_distance = 8 - n_distance

        for i in range(2 ** n_distance):
            j = bin(i)[2:]
            j = j.zfill(n_distance)
            j = [int(it)+1 for it in j]
            s = [2]
            for k in range(n_distance):
                s.append(s[-1] + j[k])
            if s[-1] > 9:
                continue
            for k in range(pai):
                s[k] = str(s[k]) * ns[k]
            s = ''.join(s) + 'm'
            if calc_shanten(tenhou_to_vector(s)) == 0:
                _, num, l, _ = calc_ukeire(tenhou_to_vector(s))
                if len(l) > 2:
                    kind27.append(s)
                    print(s)
                    print(num, l)
                    nums.append(num)

    print(nums)
    nums = []
    print('=============')
    for kind in kind27:
        kind = kind[:-1]
        m = 7 - (int(kind[-1]) - int(kind[0]))
        kind = [str(m+int(it)) for it in kind]
        kind = ''.join(kind) + 'm'
        _, num, l, _ = calc_ukeire(tenhou_to_vector(kind))
        print(kind)
        print(num, l)
        nums.append(num)
    print(nums)