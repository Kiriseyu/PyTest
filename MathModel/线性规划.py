from scipy.optimize import linprog

# 定义优化问题参数
profit_coefficients = [-100, -150]  # 最大化利润需取负（因linprog默认求最小值）
constraint_matrix = [
    [3, 2],  # 资源1约束：3A + 2B ≤ 180
    [2, 4]  # 资源2约束：2A + 4B ≤ 160
]
resource_limits = [180, 160]
variable_bounds = [(0, None), (0, None)]  # 非负约束

# 求解线性规划问题
result = linprog(
    c=profit_coefficients,
    A_ub=constraint_matrix,
    b_ub=resource_limits,
    bounds=variable_bounds,
    method='highs'  # 使用HiGHS求解器（SciPy 1.6+推荐）
)

# 解析并格式化结果
if result.success:
    # 注意：结果需要取反转换回最大化问题的解
    optimal_production = {
        'A': -result.x[0],
        'B': -result.x[1]
    }
    max_profit = -result.fun

    print(f"最优生产方案：")
    print(f"产品A产量：{optimal_production['A']:.1f} 单位")
    print(f"产品B产量：{optimal_production['B']:.1f} 单位")
    print(f"最大利润：{max_profit:.1f} 元")
else:
    print("未找到可行解，请检查约束条件是否合理")