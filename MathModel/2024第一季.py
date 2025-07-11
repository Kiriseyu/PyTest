# model_problem1_case1_fixed.py
import pandas as pd
import pulp
from pathlib import Path

# ------------------------------------------------------------------
# 1. 路径
# ------------------------------------------------------------------
CLEAN_DIR = Path(r"C:\Users\26790\Desktop\Result\CleanResult")

# ------------------------------------------------------------------
# 2. 读入清洗数据
# ------------------------------------------------------------------
stats   = pd.read_csv(CLEAN_DIR / "stats_clean.csv")
land    = pd.read_csv(CLEAN_DIR / "land_clean.csv")
sales   = pd.read_csv(CLEAN_DIR / "sales_clean.csv")
initial = pd.read_json(CLEAN_DIR / "initial_2023.json")

# ------------------------------------------------------------------
# 3. 建立快速索引
# ------------------------------------------------------------------
# 3-1 地块面积
area_dict = dict(zip(land["plot_name"], land["area"]))

# 3-2 地块类型
land_type_dict = dict(zip(land["plot_name"], land["land_type"]))

# 3-3 作物-地块-季次 参数
param = {(r.crop_name, r.land_type, r.season):
         (r.yield_per_mu, r.cost_per_mu, r.price_per_kg)
         for _, r in stats.iterrows()}

# 3-4 预期销售量
sales_dict = dict(zip(sales["crop_name"], sales["expected_sales"]))

# 3-5 豆类集合
legume_set = {"黄豆", "黑豆", "红豆", "绿豆", "爬豆",
              "豇豆", "刀豆", "芸豆"}

# ------------------------------------------------------------------
# 4. 集合
# ------------------------------------------------------------------
years   = [2024]                    # 先跑一年
seasons = ["第一季", "第二季"]
plots   = land["plot_name"].tolist()
crops   = sales["crop_name"].unique().tolist()

# ------------------------------------------------------------------
# 5. 创建 PuLP 模型
# ------------------------------------------------------------------
m = pulp.LpProblem("PlantSchedule_P1C1_Fixed", pulp.LpMaximize)

# 5-1 种植面积
a = pulp.LpVariable.dicts("a",
                          ((l, c, y, s) for l in plots
                                         for c in crops
                                         for y in years
                                         for s in seasons),
                          lowBound=0)

# 5-2 是否种植（二进制）
z = pulp.LpVariable.dicts("z",
                          ((l, c, y) for l in plots
                                      for c in crops
                                      for y in years),
                          cat="Binary")

# 5-3 实际销售量（≤预期需求）
sales_var = pulp.LpVariable.dicts("sales",
                                  ((c, y) for c in crops for y in years),
                                  lowBound=0)

# ------------------------------------------------------------------
# 6. 目标函数：max 销售收入 - 种植成本
# ------------------------------------------------------------------
m += pulp.lpSum(
        sales_var[c, y] * price
        - a[l, c, y, s] * cost
        for (c, lt, ss), (yield_, cost, price) in param.items()
        for l in plots
        for y in years
        for s in seasons
        if land_type_dict[l] == lt
)

# ------------------------------------------------------------------
# 7. 约束
# ------------------------------------------------------------------
BIG_M = 1e6
EPS   = 1e-3

for y in years:
    for s in seasons:
        for l in plots:
            lt = land_type_dict[l]

            # 7-1 地块面积
            m += pulp.lpSum(a[l, c, y, s]
                            for c in crops
                            if (c, lt, s) in param) <= area_dict[l]

            for c in crops:
                # 不可种作物强制为 0
                if (c, lt, s) not in param:
                    m += a[l, c, y, s] == 0
                    continue

                # 7-2 面积与二进制变量链接
                m += a[l, c, y, s] <= BIG_M * z[l, c, y]
                m += a[l, c, y, s] >= EPS * z[l, c, y]

                # 7-3 重茬约束（可选）
                # if str(y-1) in initial.get(l, {}) and initial[l][str(y-1)] == c:
                #     m += z[l, c, y] == 0

    # 7-4 销售量 ≤ 预期需求 & ≤ 产量
    for c in crops:
        total_yield = pulp.lpSum(
            a[l, c, y, s] * param[(c, land_type_dict[l], s)][0]
            for l in plots
            for s in seasons
            if (c, land_type_dict[l], s) in param
        )
        m += sales_var[c, y] <= sales_dict.get(c, 0)
        m += sales_var[c, y] <= total_yield

    # 7-5 三年豆类约束——仅当该地块-季节存在可行豆类才设约束
    for l in plots:
        lt = land_type_dict[l]
        feasible_legume = [c for c in legume_set
                           if (c, lt, "第一季") in param or (c, lt, "第二季") in param]
        if feasible_legume:            # 有豆类才建约束
            m += pulp.lpSum(z[l, c, y]
                            for c in feasible_legume) >= 1

# ------------------------------------------------------------------
# 8. 求解
# ------------------------------------------------------------------
m.solve(pulp.PULP_CBC_CMD(msg=0))
print("Status :", pulp.LpStatus[m.status])
print("Objective =", pulp.value(m.objective))

# ------------------------------------------------------------------
# 9. 结果整理并导出
# ------------------------------------------------------------------
records = []
for l in plots:
    for c in crops:
        for s in seasons:
            val = a[l, c, 2024, s].varValue
            if val and val > 0.01:
                records.append({"地块名": l, "作物": c, "季次": s, "面积": val})

result = pd.DataFrame(records)
result.to_excel(CLEAN_DIR / "result1_1_2024_only.xlsx", index=False)