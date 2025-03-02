import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# 使用之前定义的数据
store1 = [10, 14, 19, 22, 26, 31, 31, 34, 37, 41, 45, 47, 55, 55, 57, 62, 67, 69, 73, 78, 83, 88, 90]
store2 = [11, 13, 17, 23, 25, 28, 30, 32, 35, 36, 39, 42, 48, 51, 52, 58, 60, 64, 64, 75, 79, 84, 87]

# 创建Q-Q图
plt.figure(figsize=(8, 6))
store1_sorted = np.sort(store1)
store2_sorted = np.sort(store2)

plt.scatter(store2_sorted, store1_sorted)
plt.plot([min(store2), max(store2)], [min(store1), max(store1)], 'r--')  # 添加参考线

plt.title('Q-Q Plot: Store 1 vs Store 2')
plt.xlabel('Store 2 Quantiles')
plt.ylabel('Store 1 Quantiles')
plt.grid(True)

plt.show()

# 计算方差和标准差
var1 = np.var(store1)
std1 = np.std(store1)
var2 = np.var(store2)
std2 = np.std(store2)

print("Store 1:")
print(f"Variance: {var1:.2f}")
print(f"Standard Deviation: {std1:.2f}")
print("\nStore 2:")
print(f"Variance: {var2:.2f}")
print(f"Standard Deviation: {std2:.2f}")

