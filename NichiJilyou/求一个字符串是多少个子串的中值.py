# n, c = input().split()
# n = int(n)
# s = input()
# while True:
#     if len(s) <= n and str.islower:
#         break
#     else:
#         continue
# lenth = len(s)
# if lenth % 2 == 0:
#     c1 = s[lenth // 2 - 1]
#     print(len(s[:3:]))
# else:
#     c2 = s[lenth // 2]
#     print(c2)

a, b = map(str, input().split())
ss = str(input())
a = int(a)
aa = ss.count(b)
for i in range(a):
    if ss[i] == b:
        aa += min(i, a-i-1)
        print(aa)
        