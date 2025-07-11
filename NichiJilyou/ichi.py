import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

data = {
    "企业名称": ["西曲矿", "西井矿", "官地矿", "白家庄矿", "杜尔坪矿"],
    "原煤成本": [97.21, 101.11, 103.69, 99.89, 103.69],
    "原煤引润": [88.36, 143.96, 124.78, 96.91, 124.78],
    "原煤产量": [100.64, 100.94, 101.85, 102.63, 101.85],
    "原煤销售量": [91.90, 104.39, 103.16, 102.37, 103.16],
    "产品效益": [85.21, 94.33, 106.39, 98.47, 106.39],
    "全员效率": [158.61, 121.91, 137.16, 87.51, 137.16],
    "流动资金周转天数": [204.52, 171.31, 142.63, 108.35, 142.63],
    "百万吨死亡率": [100.22, 99.13, 97.65, 71.67, 97.65]
}

df = pd.DataFrame(data)

scaler = StandardScaler()
df_scaled = pd.DataFrame(scaler.fit_transform(df.drop(columns=["企业名称"])), columns=df.columns[1:])

weights = {
    "原煤成本": -0.2,
    "原煤引润": 0.1,
    "原煤产量": 0.2,
    "原煤销售量": 0.2,
    "产品效益": 0.15,
    "全员效率": 0.1,
    "流动资金周转天数": -0.05,
    "百万吨死亡率": -0.1
}

df_scaled["score"] = np.dot(df_scaled, list(weights.values()))
df_scaled["rank"] = df_scaled["score"].rank(ascending=False)

final_df = df[["企业名称"]].join(df_scaled[["score", "rank"]])

print(final_df)
