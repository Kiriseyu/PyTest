from scipy.optimize import linprog
c = [-3, -4, -6]
A = [[2, 3, 4.2], [2.8, 2.5, 3.5]]
b = [500, 600]
x_bounds = [(12, None), (10, None), (6, None)]
result = linprog(c, A_ub=A, b_ub=b, bounds=x_bounds, method='highs')
max_profit = -result.fun
print(f"最大利润为：{max_profit
:.2f}单位")