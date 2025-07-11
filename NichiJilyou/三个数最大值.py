# a, b, c = map(int, input().split())
# for i in range(3):
#     if a > b:
#         b = a
#     if b > c:
#         c = b
#     else:
#         a = c
#     break
# print(a)

# or

a, b, c = map(int, input().split())
print(max(a, b, c))
