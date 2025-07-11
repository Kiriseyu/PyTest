# abs() 函数返回数字的绝对值。
# abs( '数值表达式' )

# all()判断给定的可迭代参数 iterable 中的所有元素是否都为 TRUE
# all(iterable'元组或列表')

# any() 判断给定的可迭代参数 iterable 是否全部为 False
# any(iterable'元组或列表')

# basestring() str 和 unicode 的超类（父类），也是抽象类，因此不能被调用和实例化，但可以被用来判断一个对象是否为 str 或者 unicode 的实例
# 注意：Python3 不支持 basestring() 函数，改用 str() 函数。
# basestring()

# bin() 返回一个整数 int 或者长整数 long int 的二进制表示。
# bin('int 或者 long int 数字')

# bool() 函数用于将给定参数转换为布尔类型，如果没有参数，返回 False。bool 是 int 的子类。
# class bool(['要进行转换的参数'])

# bytearray() 方法返回一个新字节数组。这个数组里的元素是可变的，并且每个元素的值范围: 0 <= x < 256。

# class bytearray([source'源库'[, encoding'编码'[, errors‘错误’]]])
# 如果source为整数，则返回一个长度为source的初始化数组；
# 如果source为字符串，则按照指定的encoding将字符串转换为字节序列；
# 如果source为可迭代类型，则元素必须为[0, 255]中的整数；
# 如果source为与buffer接口一致的对象，则此对象也可以被用于初始化bytearray。
# 如果没有输入任何参数，默认就是初始化数组为0个元素。

# callable()

# chr()ASCII转字符

# classmethod

# cmp(x,y) 函数用于'比较'2个对象，如果 x < y 返回 -1, 如果 x == y 返回 0, 如果 x > y 返回 1。

# compile() 函数将一个字符串编译为字节代码。

# compile() 函数将一个字符串编译为字节代码。

# complex() 函数用于创建一个值为 real + imag * j 的复数或者转化一个字符串或数为复数。如果第一个参数为字符串，则不需要指定第二个参数。

# delattr 函数用于删除属性。

# dict() 函数用于创建一个字典。
# class dict(**kwarg'关键字')
# class dict(mapping'元素的容器', **kwarg)
# class dict(iterable'可迭代对象', **kwarg)

# dir()
# dir()   #  获得当前模块的属性列表
# dir([])  # 查看列表的方法

# python divmod()把除数和余数运算结果结合起来，返回一个包含商和余数的元组(a // b, a % b)

# enumerate()

# eval()执行一个字符串表达式，并返回表达式的值。
# eval(expression'表达式'[, globals'变量作用域，必须是一个字典对象'[, locals'任何映射对象']])

# execfile()

# file()

# filter()

# float()整数和字符串转换成浮点数。

# str.format()通过 {} 和 : 来代替以前的 % 。

# frozenset()

# getattr()

# globals()

# hasattr()

# hash()获取取一个对象（字符串或者数值等）的哈希值。

# help()查看函数或模块用途的详细说明。

# hex()10进制整数转换成16进制，以字符串形式表示

# id()获取对象的内存地址

# input()接受一个标准输入数据，返回为 string 类型

# int()将一个字符串或数字转换为整型。

# isinstance()判断一个对象是否是一个已知的类型，类似 type()。
# isinstance(object'实例对象', classinfo'是直接或间接类名、基本类型或者由它们组成的元组。')

# issubclass()

# iter()

# len()返回对象（字符、列表、元组等）长度或项目个数。

# list()将元组转换为列表。
# 元组与列表是非常类似的，区别在于元组的元素值不能修改，元组是放在括号中，列表是放于方括号中。

# locals()

# long()数字或字符串转换为一个长整型

# map()根据提供的函数对指定序列做映射
# map(function'函数', iterable'一个或多个序列', ...)

# max()返回给定参数的最大值，参数可以为序列

# memoryview()

# min()返回给定参数的最小值，参数可以为序列。

# next()返回迭代器的下一个项目。要和生成迭代器的 iter() 函数一起使用。
# next(iterable'可迭代对象'[, default])
# default -- 可选，用于设置在没有下一个元素时返回该默认值，如果不设置，又没有下一个元素则会触发 StopIteration 异常。

# object()返回一个空对象，我们不能向该对象添加新的属性或方法。

# oct()函数将一个整数转换成 8 进制字符串

# open()打开一个文件，创建一个 file 对象，相关的方法才可以调用它进行读写。

# ord()返回对应的 ASCII 数值，或者 Unicode 数值

# pow()方法返回 xy（x 的 y 次方） 的值。
# import math
# math.pow( x, y )
# '或者'
# pow(x, y[, z])

# print()打印输出
# print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False)
# objects -- 复数，表示可以一次输出多个对象。输出多个对象时，需要用 , 分隔。
# sep -- 用来间隔多个对象，默认值是一个空格。
# end -- 用来设定以什么结尾。默认值是换行符 \n，我们可以换成其他字符串。
# file -- 要写入的文件对象。
# flush -- 输出是否被缓存通常决定于 file，但如果 flush 关键字参数为 True，流会被强制刷新。

# property()

# range()创建一个整数列表，一般用在 for 循环中
# range(start, stop[, step])

# raw input()

# reduce()会对参数序列中元素进行累积。
# reduce(function'函数', iterable'可迭代对象'[, initializer'可选，初始参数'])

# reload()

# repr()

# reverse()反向列表中元素。
# list.reverse()

# round()返回浮点数x的四舍五入值。
# round( x [, n]  )

# set()创建一个无序不重复元素集，可进行关系测试，删除重复数据，还可以计算交集、差集、并集等。
# class set([iterable])

# setattr()

# slice()

# sorted()对所有可迭代的对象进行排序操作。
# sorted(iterable'可迭代对象。', cmp=None' 比较的函数', key=None'用来进行比较的元素', reverse=False'')
# reverse = True 降序 ， reverse = False 升序（默认)

# staticmethod()

# str()字符串

# sum()对序列进行求和计算。
# sum(iterable‘可迭代对象’[, start])

# super()调用父类(超类)的一个方法。
# 解决多重继承问题的，直接用类名调用父类方法在使用单继承的时候没问题，但是如果使用多继承，会涉及到查找顺序（MRO）、重复调用（钻石继承）等种种问题。

# tuple()将列表转换为元组。
# tuple( iterable )


# type()

# unichr()

# unicode()

# vars()

# xrange()

# zip()

# __import__()用于动态加载类和函数

# exec obj
