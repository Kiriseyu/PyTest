def factors(x):
    factors = []
    i = 2
    while i * i <= x:
        if x % i:
            i += 1
        else:
            x //= i
            factors.append(i)
    if x > 1:
        factors.append(x)
    return factors
num = int(input())
print(len(set(factors(num))))
