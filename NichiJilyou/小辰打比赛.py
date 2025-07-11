n, x = map(int, input().split())
a = list(map(int, input().split()))
a.sort()
sum = 0
for i in range(n):
    if x > a[i]:
        sum += a[i]
print(sum)