import numpy as np

# 数据点
points = {
    'x1': [0, -1],
    'x2': [3, 0],
    'x3': [5, 2],
    'x4': [1, 1],
    'x5': [10, 5]
}

# 查询点
query = np.array([2, 1])

# 1. Manhattan距离计算
def manhattan_distance(p1, p2):
    return np.sum(np.abs(p1 - p2))

# 2. Euclidean距离计算
def euclidean_distance(p1, p2):
    return np.sqrt(np.sum((p1 - p2) ** 2))

# 3. Cosine相似度计算
def cosine_similarity(p1, p2):
    return np.dot(p1, p2) / (np.linalg.norm(p1) * np.linalg.norm(p2))

# 计算所有距离
print("Manhattan distances:")
for name, point in points.items():
    dist = manhattan_distance(np.array(point), query)
    print(f"{name}: {dist:.2f}")

print("\nEuclidean distances:")
for name, point in points.items():
    dist = euclidean_distance(np.array(point), query)
    print(f"{name}: {dist:.2f}")

print("\nCosine similarities:")
for name, point in points.items():
    sim = cosine_similarity(np.array(point), query)
    print(f"{name}: {sim:.4f}") 