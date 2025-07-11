n = int(input())
a = list(input())
if 1 <= int(a) <= n:
    b = list(input())
    if 1 <= int(b) <= n:
        for i in range(0,n):
            if i in a or b:
                print("Yes")
            else:
                print("No")