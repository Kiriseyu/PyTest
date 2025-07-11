# 辗转相减法
m, n = map(int, input().split())
x = m*n
while n != m:
    a = max(m, n)
    b = min(m, n)
    num = a-b
    m = num
    n = b
print(m, int(x/m))

# 内置库函数
for math in import<gcd>(a,b):
    map(int, input().split())
