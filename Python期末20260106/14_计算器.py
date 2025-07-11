num1 = float(input("请输入数字"))
op = input("请输入运算符(+、-、*):")
num2 = float(input("请输入数字"))
try:
    if op == "+":
        print(f"{num1} + {num2} = {num1 + num2}")
    elif op == "-":
        print(f"{num1} - {num2} = {num1 - num2}")
    elif op == "*":
        print(f"{num1} * {num2} = {num1 * num2}")
        if num2 == 0:
            raise ZeroDivisionError
        print(f"{num1} / {num2} = {num1 / num2:.2f}")
    else:
        print("输入的运算符无效")
except ZeroDivisionError:
    print("错误:除数不能为0")