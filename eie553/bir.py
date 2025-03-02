def birthday_probability(q, N):
    # 初始化概率为1
    probability = 1.0
    
    # 计算连乘项
    for i in range(1, q):
        probability *= (1 - i/N)
    
    # 返回1减去连乘的结果
    return 1 - probability

# 计算46个学生，10000种可能的概率
q = 46
N = 10000

result = birthday_probability(q, N)
print(f"The probability is approximately: {result:.4f}")
print(f"The probability percentage is: {result*100:.2f}%")