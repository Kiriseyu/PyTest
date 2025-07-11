# if-elif-else法
i = int(input())
if i <= 100000:
    x = i*0.1
elif i <= 200000:
    x = 100000*0.1+(i-100000)*0.075
elif i <= 400000:
    x = 100000*0.1+100000*0.075+(i-200000)*0.05
elif i <= 600000:
    x = 100000*0.1+100000*0.075+200000*0.05+(i-400000)*0.03
elif i <= 1000000:
    x = 100000*0.1+100000*0.075+200000*0.05+200000*0.03+(i-600000)*0.015
else:
    x = 100000*0.1+100000*0.075+200000*0.05+200000*0.03+400000*0.015+(i-1000000)*0.01
print(int(x))

# 数组分段计算
profit = [0, 100000, 200000, 400000, 600000, 1000000]
# 利润
rate = [0.1, 0.75, 0.05, 0.03, 0.015, 0.01]
# 比率
income = int(input())
# 收入
i = 1
j = 1
summer = 0
while profit[i] < income:
    summer = summer + (profit[i]-profit[i-1])*rate[j-1]
    i += 1
    j += 1
summer += (income-profit[i-1])*rate[j-1]
print(int(summer))

# 使用递归实现
a = int(input())


def func(n):
    if n <= 100000:
        result = n*0.1
    elif 100000 < n <= 200000:
        result = func(100000)+(n-100000)*0.075
    elif 200000 < n <= 400000:
        result = func(200000)+(n-200000)*0.05
    elif 400000 < n <= 600000:
        result = func(400000)+(n-400000)*0.03
    elif 600000 < n <= 1000000:
        result = func(600000)+(n-600000)*0.015
    else:
        result = func(1000000)+(n-1000000)*0.01
    return result


print(int(func(a)))
