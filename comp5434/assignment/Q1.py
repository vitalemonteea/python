import numpy as np
from fractions import Fraction

# 创建随机游走矩阵
M = np.array([
    [0, 1, 0, 0, 0],    # A -> B
    [0, 0, 1, 1, 0],    # B -> C,D
    [1, 0, 0, 0, 1],    # C -> A,E
    [0, 0, 0, 0, 1],    # D -> B,E
    [1, 1, 0, 1, 0]     # E -> A,D
])

# 计算基础转移概率矩阵 (按列计算)
M_prob = M / M.sum(axis=0, keepdims=True)

# 加入阻尼因子，构造最终的转移概率矩阵
damping_factor = 0.8
n = len(M)
teleport_matrix = np.full((n, n), 1/n)
M_prob = damping_factor * M_prob + (1 - damping_factor) * teleport_matrix

print("\nTransition Probability Matrix M_prob:")
for row in M_prob:
    print([Fraction(x).limit_denominator() for x in row])

# 初始化PageRank值（均匀分布）
r = np.array([0.2, 0.2, 0.2, 0.2, 0.2])

# 迭代计算PageRank
iterations = 100
print("\nInitial r:", [Fraction(x).limit_denominator() for x in r])
for i in range(iterations):
    r_new = M_prob @ r
    print(f"Iteration {i+1}:", [Fraction(x).limit_denominator() for x in r_new])
    if np.allclose(r, r_new, atol=1e-10):
        print(f"\nConverged after {i+1} iterations!")
        break
    r = r_new

print("\nFinal PageRank values:")
print("A: {:.2f}".format(r[0]))
print("B: {:.2f}".format(r[1]))
print("C: {:.2f}".format(r[2]))
print("D: {:.2f}".format(r[3]))
print("E: {:.2f}".format(r[4]))

# 验证和为1
print("\nSum of PageRank values: {:.2f}".format(sum(r)))
