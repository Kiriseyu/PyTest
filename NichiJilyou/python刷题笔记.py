#1.类型转换
a=input()
print(a.lower())       #全小写
print(a.upper())			 #全大写
print(a.title())       #首字母大写

a=int(input())
print(hex(a))          #十进制转换十六进制
print(bin(a))					 #十进制转化二进制
print(ord(a))          #字母转数字

str = input()
print(str.isalpha())    #是否只包含字符
print(str.isdigit())    #是否只包含数字
print(str.isspace())    #是否只包含空格

a=float(input())
print(round(a,2))       #保留两位小数


#2.列表
list.insert(0,'a')     #在list的第一个位置插入a
list.reverse()          #将list的元素倒置
a in list1              #查询a是否在list1中
b=[int(i) for i in a]   #将列表a中的字符串变成数字


#3.字典
operator_dict={'<':'less than','==':'equal'}           #设置字典
print('Here is the original dict:')
for x in sorted(operator_dict):
   print(f'Operator {x} means {operator_dict[x]}.')
print(" ")
operator_dict['>']='greater than'											 #添加到字典中
print("The dict was changed to:")
for x in sorted(operator_dict):
   print(f'Operator {x} means {operator_dict[x]}.')    #operator_dict[x]是输出字典的值

result_dict={'Allen': ['red', 'blue', 'yellow'],'Tom': ['green', 'white', 'blue'],'Andy': ['black', 'pink']}
for i in sorted(result_dict):
    print(f"{i}'s favorite colors are:")
    for j in result_dict[i]:
       print(j)

name=input().split()
langue=input().split()
dict1=zip(name,langue)
print(dict(dict1))
#zip () 函数用于将可迭代的对象作为参数，将对象中对应的元素打包成一个个元组，
#然后返回由这些元组组成的列表.得到列表，将列表转化为字典

dict1 = {
    "a": ["apple", "abandon", "ant"],
    "b": ["banana", "bee", "become"],
    "c": ["cat", "come"],
    "d": "down",
}
letter = input()
word = input()
if letter in dict1:
    dict1[letter].append(word)     #将值word添加到键letter中
    print(dict1)
else:
    dict1.update({letter: word})   #添加键值对0
    print(dict1)


#4.类函数
