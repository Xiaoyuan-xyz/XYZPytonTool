def find_max_clique(graph):
    # 构建邻接表，每个顶点的邻居集合
    adj = {v: set(neighbors) for v, neighbors in graph.items()}
    max_clique = set()  # 存储当前找到的最大团

    def bronkkerbosch(R, P, X):
        # if len(P) > 0:
        #     print(len(P))
        nonlocal max_clique
        # 如果P和X都为空，当前R是一个极大团
        if not P and not X:
            if len(R) > len(max_clique):
                max_clique = set(R)
            return
        # 选择枢轴点u（P和X中的任一顶点）
        u = next(iter(P | X)) if (P | X) else None
        # 确定候选顶点集合
        candidates = P - adj[u] if u is not None else P.copy()
        # 遍历所有候选顶点
        for v in list(candidates):  # 转换为列表避免遍历时修改集合
            # 递归调用：添加v到R，更新P和X为与v相邻的顶点
            bronkkerbosch(R | {v}, P & adj[v], X & adj[v])
            # 将v从P移除，并添加到X中
            P.remove(v)
            X.add(v)

    # 初始调用：R为空，P为所有顶点，X为空
    bronkkerbosch(set(), set(adj.keys()), set())
    # 返回最大团的顶点列表（按编号排序）
    return sorted(max_clique) if max_clique else []


# 示例输入
example_graph = {
    0: [1, 4, 5],
    1: [0, 2, 4],
    2: [1, 4],
    3: [4],
    4: [0, 1, 2, 3, 5],
    5: [0, 4],
}

with open(
    r"G:\Program\PytonTool\question20250415\现代汉语大词典.txt",
    "r",
    encoding="utf-8",
) as f:
    words = f.readlines()

words = [word.strip() for word in words]
words = [word for word in words if len(word) == 2]

# 打乱列表
import random
random.shuffle(words)

print(len(words))

graph = {}


for word in words:
    zi1 = word[0]
    zi2 = word[1]
    if zi1 not in graph:
        graph[zi1] = []
    if zi2 not in graph:
        graph[zi2] = []
    if zi2 not in graph[zi1]:
        graph[zi1].append(zi2)
    if zi1 not in graph[zi2]:
        graph[zi2].append(zi1)

print(len(graph))

# 调用函数并打印结果
print(find_max_clique(graph))  # 输出：[1, 2, 3]

