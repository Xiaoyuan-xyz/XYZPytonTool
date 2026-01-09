import random

now = 150
times = 4
sup = 400
inf = 0

def test(now, times, sup, inf):
    for i in range(times):
        now += random.randint(1, 100)
        now -= random.randint(1, 100)
    return now > sup // 2

result = {0: 0, 1: 0, -1: 0}

n = 10000
for i in range(n):
    result[test(now, times, sup, inf)]+=1

print(result)
    