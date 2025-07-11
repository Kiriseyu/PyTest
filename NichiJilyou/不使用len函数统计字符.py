str1 = "itheima"
str2 = "itcast"
str3 = "python"

# 定义一个计数变量
count = 0
for i in str1:
    count += 1
print(f"字符串{str1}的长度是:{count}")
count = 0
for m in str2:
    count += 1
print(f"字符串{str2}的长度是:{count}")
count = 0
for z in str3:
    count += 1
print(f"字符串{str3}的长度是:{count}")

# 增加函数的复用性，用函数优化


def my_len(data):
    counts = 0
    for i in data:
        counts += 1
    print(data, counts)


my_len(str1)
my_len(str2)
my_len(str3)


def prompt():
    print("欢迎来到黑马程序员！\n请出示您的健康吗以及72小时核酸证明！")


prompt()
