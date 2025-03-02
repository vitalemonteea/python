def hex_to_int(hex_str):
    return int(hex_str, 16)

# 扩展欧几里得算法
def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

# 计算模乘法逆元
def mod_inverse(e, phi):
    gcd, x, y = extended_gcd(e, phi)
    if gcd != 1:
        raise Exception('模乘法逆元不存在')
    else:
        return x % phi

# 转换16进制为整数
p = hex_to_int('F7E75FDC469067FFDC4E847C51F452DF')
q = hex_to_int('E85CED54AF57E53E092113E62F436F4F')
e = hex_to_int('0D88C3')

# 计算φ(n)
phi = (p - 1) * (q - 1)

# 计算私钥d
d = mod_inverse(e, phi)

print(f"p = {p}")
print(f"q = {q}")
print(f"e = {e}")
print(f"φ(n) = {phi}")
print(f"d = {d}")
print(f"d (hex) = {hex(d)[2:].upper()}")