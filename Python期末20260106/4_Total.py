total = 0
for i in range(1,101):
    if i % 3 == 0 or i % 5 == 0:
        total += i
for j in range(1,101):
    if j % 3 == 0 or j % 5 == 0:
        print(j,end = " ")
print(total)