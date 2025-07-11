import numpy as np
def f(x):
    return x - 1/x + 5
x_max = 10
max_value = f(x_max)
max_value_rounded = round(max_value, 2)
print(f"函数f(x)=x-1/x+5在区间[1,10]上的最大值：")
print(f"f(10) = {max_value:.2f}")
print(f"保留两位小数：{max_value_rounded:.2f}")
test_points = np.linspace(1.1, 9.9, 10)
derivatives = [1 + 1/(x**2) for x in test_points]
print("\n单调性验证：")
print(f"在测试点上导数均为正，最小导数值: {min(derivatives):.4f} > 0")