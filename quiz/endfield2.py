from fractions import Fraction

MAX_STEPS = 6
LOW = Fraction(1, 24)
HIGH = Fraction(1, 10)

def generate():
    # 每个状态保存：
    # (当前已生成数集合, 已用步骤数, 是否用过除以5)
    initial = (frozenset([Fraction(1, 1)]), 0, False)

    results = set()
    visited = set()

    stack = [initial]

    while stack:
        nums, steps, used_div5 = stack.pop()

        # 去重状态
        state_key = (nums, steps, used_div5)
        if state_key in visited:
            continue
        visited.add(state_key)

        # 记录区间内的值
        for x in nums:
            if LOW <= x <= HIGH:
                results.add(x)

        if steps >= MAX_STEPS:
            continue

        nums_list = list(nums)

        # 尝试单目运算
        for x in nums_list:
            # 除以2
            new_nums = set(nums)
            new_nums.add(x / 2)
            stack.append((frozenset(new_nums), steps + 1, used_div5))

            # 除以3
            new_nums = set(nums)
            new_nums.add(x / 3)
            stack.append((frozenset(new_nums), steps + 1, used_div5))

            # 除以5（只能一次）
            if not used_div5:
                new_nums = set(nums)
                new_nums.add(x / 5)
                stack.append((frozenset(new_nums), steps + 1, True))

        # 尝试加法（任意两数）
        for i in range(len(nums_list)):
            for j in range(i, len(nums_list)):
                a = nums_list[i]
                b = nums_list[j]
                new_nums = set(nums)
                new_nums.add(a + b)
                stack.append((frozenset(new_nums), steps + 1, used_div5))

    return sorted(results)


if __name__ == "__main__":
    values = generate()
    for v in values:
        print(v)
