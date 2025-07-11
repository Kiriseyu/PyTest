# lambda三元法
print((lambda x: 'A' if x >= 90 else 'B' if x >= 80 else 'C' if x >= 70 else 'D' if x >= 60 else 'E')(int(input())))

# if-else语法
x = int(input())
if x < 60:
    print("E")
elif 60 <= x < 70:
    print("D")
elif 70 < x < 80:
    print("C")
elif 80 <= x < 90:
    print("B")
else:
    print("A")
