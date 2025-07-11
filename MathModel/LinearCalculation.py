from pulp import *

# 定义线性规划问题
PB = LpProblem("Production_Optimization", LpMaximize)
# 构造函数
x1 = LpVariable("x1", 0, None, LpContinuous)
x2 = LpVariable("x2", 0, None, LpContinuous)
x3 = LpVariable("x3", 0, None, LpContinuous)
# 添加目标函数
PB += 1000 * x1 + 2000 * x2 + 3000 * x3, "Total_Profit"
# 添加约束条件
PB += x1 + 2 * x2 + 3 * x3 <= 10
PB += 0 * x1 + x2 + 2 * x3 <= 5
# 写入LP文件
PB.writeLP("Production_Optimization.lp")
# 模型求解
PB.solve()
# 结果显示
# check status:pulp.LpStatus[PB.status]
print("\n", "status:", LpStatus[PB.status], "\n")
for v in PB.variables():
    print("t", v.name, "=", v.varValue, "tons", "\n")
print("Maximize Daily Profit =", "Rs", value(PB.objective))
