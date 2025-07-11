# [竞赛入门]简单的a+b 输入两个整数a和b计算a+b的和
# while True:
#     try:
#         a, b = map(int, input().strip().split())
#         if a > 2**10 or b > 2**10:
#             break
#         print(a+b)
#     except Exception:
#         break

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
# team = list(map(int,input().split())) f啊

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

# 小乐乐的班级进行了一次期中考试，考试一共有3门科目：数学，语文，英语，小乐乐的班主任决定给没有通过考核的同学家长开一次家长会，考核的标准是三科平均分不低于60分，所以现在想请你帮忙算一算小乐乐会不会被叫家长。
# 一行，输入三个整数（表示小乐乐的数学、语文、英语的成绩），用空格分隔。
# 一行，如果小乐乐会被请家长则输出“YES”，否则输出“NO”。
# a, b, c = map(int, input().split())
# if (a+b+c)/3 >= 60:
#     print("NO")
# else:
#     print("YES")

# a, b = map(int, input().strip().split())
#
# str.count(sub, start = 0,end = len(string))

# 试计算在区间 1 到 n的所有整数中，数字x(0 ≤ x ≤ 9)共出现了多少次？例如，在 1到11中，即在 1,2,3,4,5,6,7,8,9,10,11 中，数字 1 出现了 4 次。
# End, Num = (int(i.strip()) for i in input().split())
# Count = []
# for i in range(1, End + 1):
#     Count.extend(list(str(i)))
# Times = Count.count(str(Num))
# print(Times)

# a, b = map(int, input().split())
# list1 = []
# for i in range(1, a+1):
#     list1.append(i)
# # a = str(str)
# a = str(list1)
# # b = a.count(Num)
# print(a.count(str(b)))
# print(list1)

# 循环
# if  # elif  # else

# for i in range(3):
#     print(i)

# while 条件：   #只要条件为真，就不断循环(记得结束语句,不然会陷入死循环)
#     print(xxxxx)

# count = 0                              while死循环示例
# while True:
#     print(f"第{count}次循环")
#     count +=1

# for i in range(1,6):                   continue的用法示例
#     for j in range(1,3):
#         if i==3:
#             continue
#         print(f"{i}层-{i}0{j}室")

# for i in range(1,6):                   break的用法示例
#     for j in range(1,3):
#         if i==3:
#             continue   #跳过第三层，从第四层开始
#         if i==2 and j==2:
#             break      #当dao2层2室的时候直接退出二层循环。从三层开始走
#         print(f"{i}层-{i}0{j}室")

# while True:
#     try:
#         a, b = map(int, input().strip().split())
#         if a > 2 ** 10 or b > 2 ** 10:
#             break
#         print(a+b)
#     except Exception:
#         break

# 多行输入方法
# n = int(input())
# for x in range(n):
#     s = input()

# 程序员的表白
# while True:
#     try:
#         num = int(input())
#         for i in range(num):
#             print('*', end='')
#             for i in range(num):
#                 print(' ',end='')
#             print('*', end='')
#             print()
#         for i in range(num+2):
#             print('*', end='')
#         print('\n')
#     except:
#         break

# while True:
#     try:
#         a, b = map(int, input().split())
#         print(a+b)
#     except:
#         break

# str(字符串)
# count（统计字符串里某个字符或子字符串出现的次数)
# sub(搜索的子字符串)
# start(字符串开始搜索的位置。默认为第一个字符,第一个字符索引值为0。)
# end(字符串中结束搜索的位置。字符中第一个字符的索引为 0。默认为字符串的最后一个位置。)
# range() 函数可创建一个整数列表，一般用在 for 循环中。    # 基础语法:for i in range(start,stop,step)     --->   (起始，结束，步长)
# map() 会根据提供的函数对指定序列做映射
# int 整型
# input 从用户接收输入
# split() 过指定分隔符对字符串进行切片
# strip()  strip是去除字符串中的字符，但是只去除头部和尾部的，中间的不归他管。
# ord()  >>> ord('王')#获取字符编码   # 29579
# chr()  >>> chr(29579)#把编码转成对应的字符   # '王'
# continue  程序一遇到continue，本次循环就不继续了，直接进入下一次循环
# break   只要程序遇到break，就会结束当前这个循环，注意如果是多层嵌套循环，只结束当前这一层的循环。
# try:尝试执行的代码
# except:出现错误的处理
# \t表示空4个字符，就是缩进，就是按一下tab键
# \n表示换行
# end=''表示末尾不换行
# append=是一个常用的方法，用于向列表、集合和字典等数据结构中添加元素
# len(String)  用于指定要进行长度统计的字符串，获取容器对象中元素的数量。
# set() 无顺序，不包含重复元素的集合。
# add() 向集合中添加元素，如果元素已存在，则不进行任何操作。
# update() 将一个集合中的元素添加到当前集合中，update()可以传递序列或字典作为参数，字典只会使用键
# pop() 函数用于移除列表中的一个元素(默认最后一个元素)，并且返回该元素的值
# remove(x) 删除集合中的指定元素x
# clear() 清空集合
# sorted()  sorted(iterable可迭代对象, cmp=None比较的函数, key=None用来进行比较的元素, reverse=False排序规则)
# hex()    函数用于将10进制整数转换成16进制，以字符串形式表示。


# tqdm加入进度条
# import time
# from tqdm import tqdm
#
# for i in tqdm(range(100)):
#     time.sleep(0.1)

# 标准签到：读取字符串数量
# n = input()
# result = 'ora'
# if result in n:
#     print(n.count(result))
# else:
#     print("yare yare daze")

# 1.
# n = str(input())
# r = 'ora'
# if r in n:
#     print(n.count(r))
# else:
#     print("yare yare daze")
#
# 2.
# n = int(input())
# for i in range():
#     p = str(input())
# if n > 1 and n <= 100:
#     print(p)

# 进制转换
# 2进制转8进制
# n = input()
# print(oct(int(n,2)))

# 2进制转10进制
# n = input()
# print(int(n,2))

# 2进制转16进制
# n = input()
# print(hex(int(n,2)))

# 8转2
# n=input()
# print(bin(int(n,8)))
#
# 8转10
# n=input()
# print(int(n,8))
#
# 8转16
# n=input()
# print(hex(int(n,8)))
#
# 10转2
# n=int(input())
# print(bin(n))
#
# 10转8
# n=int(input())
# print(oct(n))
#
# 10转16
# n=int(input())
# print(oct(n))
#
# 16转2
# n=input()
# print(bin(int(n,16)))
#
# 16转8
# n=input()
# print(oct(int(n,16)))
#
# 16转10
# n=input()
# print((int(n,16)))
#
# formate转2进制
# n=input()
# print((int(n,16)))
#
# 转8进制
# n=input()
# print("{:o}".format(int(n,16)))
# //先将一个16进制数转换为10进制
# //然后利用format函数格式化数字方法转换即可
#
#
# 转16进制
# n=input()
# print("{:x}".format(int(n,8)))
# //先将一个8进制的数转换为16进制
# //然后原理同上

