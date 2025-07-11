# #判断质数
n = int(input().split())
from math import sqrt
def is_prime(n):
    if n == 1:
        return False
    for i in range(2,int(sqrt(n))+1):
            if n % i == 0:
                return True
for m in range(2,n+1):
    print(is_prime)
