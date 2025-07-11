def check_prime(n):
    if n <= 1:
        return False
    for i in range(2,int(n**0.5)+1):
        if n % i == 0:
            return False
    return True
num = int(input())
if check_prime(num):
    print(f"{num}是质数")
else:
    print(f"{num}不是质数")
