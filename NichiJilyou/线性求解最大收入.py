from scipy.optimize import linprog
c = [-60, -54, -48]
A = [
    [1, 1, 1],
    [10, 8, 3],
    [1, 0, 0]
]
b = [50, 350, 20]   # 约束右侧值
x_bounds = [(0, None), (0, None), (0, None)]
result = linprog(c, A_ub=A, b_ub=b, bounds=x_bounds, method='highs')
if result.success:
    x1, x2, x3 = result.x
    max_income = -result.fun
    print(f"最优生产方案：")
    print(f"A产品：{x1:.0f}桶")
    print(f"B产品：{x2:.0f}桶")
    print(f"C产品：{x3:.0f}桶")
    print(f"最大收入：{max_income:.0f}元")
else:
    print("求解失败")