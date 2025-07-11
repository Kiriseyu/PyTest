def fibonacci(n):
    if n == 1 or n == 2:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
n = int(input("请输入要计算的斐波那契数列项数:"))
if n < 1:
    print("输入无效,n应>=1")
else:
    print(f"斐波那契数列第n项为:{fibonacci(n)}")