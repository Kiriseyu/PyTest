# [竞赛入门]简单的a+b 输入两个整数a和b计算a+b的和
# while True:
#     n = list(map(int,input().split()))
#     print(n[0]+n[1])

# [编程入门]三个数最大值 编写一个程序，输入a、b、c三个值，输出其中最大值。一行数组，分别为a b c
# lst = list(map(int,input().strip().split()))
# lst.sort()
# print(lst[2])

# [编程入门]温度转换
# # c = 5(f-32)/9
# n = float(eval(input()))
# c = 5*(n-32)/9
# print("c={:.2f}".format(c))

# [编程入门]数字逆序输出
# team = list(map(int,input().split()))
# team.reverse()
# for i in team:
#     print(i, end=' ')

# 编程入门]宏定义的练习
# a, b = map(int, input().split())
# print(a % b)

# [编程入门]分段函数求值
# x = int(input())
# if x >= 10:
#     print(3*x-11)
# elif x >= 1:
#     print(2*x-1)
# else:
#     print(x)

# [编程入门]字符串分类统计
# s = input("请输入一串字符： ")
# num, char, space, other = 0, 0, 0, 0      #分别统计数字、字母、空格、其他字符个数
# for i in s:
#     #是否为数字
#     if i.isdigit():
#         num += 1
#     #是否为字母
#     elif i.isalpha():
#         char += 1
#     elif i == ' ':
#         space += 1
#     else:
#         other += 1
# print(num, char, space, other)

# [编程入门]成绩评定
# x = int(input())
# if x < 60:
#     print("E")
# elif 60 <= x < 70:
#     print("D")
# elif 70 <= x < 80:
#     print("C")
# elif 80 <= x < 90:
#     print("B")
# else:
#     print("A")
#

# [编程入门]密码破译
# 要将"China"译成密码，译码规律是：用原来字母后面的第4个字母代替原来的字母．
# 例如，字母"A"后面第4个字母是"E"．"E"代替"A"。因此，"China"应译为"Glmre"。
# 请编一程序，用赋初值的方法使cl、c2、c3、c4、c5五个变量的值分别为，’C’、’h’、’i’、’n’、’a’，经过运算，使c1、c2、c3、c4、c5分别变为’G’、’l’、’m’、’r’、’e’，并输出。
# inp=input()
# for i in inp:
#     tmp=chr(ord(i)+4)
#     if not tmp.isalpha():
#         tmp=chr(ord(tmp)-26)
#     print(tmp,end='')

# [编程入门]水仙花数判断
# 打印出所有"水仙花数"，所谓"水仙花数"是指一个三位数，其各位数字立方和等于该本身。 例如：153是一个水仙花数，因为153=1^3+5^3+3^3。
# for j in range(100,1000):
#     ls = [int(i) for i in str(j)]
#     a = ls[0]
#     b = ls[1]
#     c = ls[2]
#     k = a**3+b**3+c**3
#     if j == k:
#         print(j)

# [编程入门]选择排序
# a = list(map(int, input().split()))
# a.sort()
# for i in a:
#     print(i)

# [编程入门]求和训练
# sum=0 #定义
# a , b , c =  map(int,input().strip().split()) # 输入数据，以空格切割
# sum = (1+a)*a/2 #求和公式
# for i in range(1,b+1): # 遍历 b
#     sum+=i*i
# for i in range(1,c+1): # 遍历 c
#     sum+=1/i
# print("{:.2f}".format(sum)) # 格式输出

# 用筛法求之N内的素数
# N = eval(input())
# for i in range(2,N):
#     for j in range(2,i):
#         if i % j == 0:
#             break
#     else:
#         print(i)

# 蓝桥杯2020年第十一届省赛真题 - 单词分析
# 小蓝正在学习一门神奇的语言，这门语言中的单词都是由小写英文字母组成，有些单词很长，远远超过正常英文单词的长度。小蓝学了很长时间也记不住一些单词，他准备不再完全记忆这些单词，而是根据单词中哪个字母出现得最多来分辨单词。
# 现在，请你帮助小蓝，给了一个单词后，帮助他找到出现最多的字母和这个字母出现的次数。
# 输入一行包含一个单词，单词只由小写英文字母组成。
# 输出两行，第一行包含一个英文字母，表示单词中出现得最多的字母是哪个。如果有多个字母出现的次数相等，输出字典序最小的那个。
# 第二行包含一个整数，表示出现得最多的那个字母在单词中出现的次数。
# s = input()
# d = dict()
# a = []
# for i in range(len(s)):
#     d[s[i]] = d.get(s[i], 0)+1
# for i in range(len(s)):
#     if d[s[i]] == max(d.values()):
#         a.append(s[i])
# print(min(a))
# print(max(d.values()))
