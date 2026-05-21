import numpy as np

np.set_printoptions(suppress=True)

# 参数
Q = 0.248  # 任取 0<Q<1
# 构造 R^T
RT = (1/4) * np.array([
    [1-Q,   0.9*Q, 0.09*Q, 0.009*Q, 0.001*Q],
    [0,     1-Q,   0.9*Q,  0.09*Q,  0.01*Q ],
    [0,     0,     1-Q,    0.9*Q,   0.1*Q  ],
    [0,     0,     0,      1-Q,     Q      ],
    [0,     0,     0,      0,       4      ]
])

# 转置得到 R
R = RT.T

# 初始向量 z
z = np.array([1, 0, 0, 0, 0], dtype=float)
e5 = np.array([0, 0, 0, 0, 1], dtype=float)

print(1/(Q**4+0.9*Q**3+0.27*Q**2+0.027*Q)*(3+Q)**4)



c = 1/((Q+3)**4/Q/(Q+0.3)**3)

print(1/c)

print(np.eye(5) - R)
print(R @ z - c*e5)
print((np.eye(5)-R)**-1)
print(np.linalg.inv((np.eye(5)-R)) @ (R @ z.T-c * e5.T))


