# 库中函数不能直接使用，需使用保留字import引用：
# import math
# math.<函数名>(...)

# 或者

# from math import <函数名>
# <函数名>(...)

# 数字常数
# math.pi == π
# math.e == e
# math.inf == ∞
# math.nan   非浮点数标记，NAN（Not a Number）

# 数值表示函数
# math.fabs(x) == |x|
# math.fmod(x,y) == x%y
# math.fsum([x,y,...]) ==x+y+...
# math.ceil(x) == 向上取整，返回不小于x的最小整数
# math.floor(x) == 向下取整，返回不大于x的最大整数
# math.factorial(x) == x! 返回x的阶乘
# math.gcd(a,b) == 返回a与b的最大公约数
# math.lcm(a,b) == 返回数字的最小公倍数
# math.modf(x) == 返回x的小数和整数部分
# math.trunc(x) == 返回x的整数部分
# math.isfinite(x) == 判断x是否为无穷大
# math.isinf(x) == 判断x是否为正数或负无穷大

# math库的幂对数函数
# math.pow(x,y) == 返回x的y次幂
# math.exp == 返回e的x次幂e是自然对数
# math.expm1(x)返回e的x次幂减1
# math.sqrt(x) == 返回x的平方根

import math
a, b = map(int, input().split())
print(math.gcd(a, b))
