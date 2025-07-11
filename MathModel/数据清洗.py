import os
import pandas as pd
from datetime import datetime

# ---------- 0. 配置 ----------
INPUT_FILE  = "工作簿1.xlsx"
SHEET_NAME  = "Sheet1"          # 真正含成分的工作表
# ---------- 0'. 统一放到独立文件夹 ----------
output_dir = "result"                 # 1. 目标文件夹名
os.makedirs(output_dir, exist_ok=True)  # 2. 若不存在就创建

OUTPUT_FILE = os.path.join(output_dir, "cleaned.xlsx")
LOG_FILE    = os.path.join(output_dir, "clean.log")

CHEM_COLS = [
    "二氧化硅(SiO2)", "氧化钠(Na2O)", "氧化钾(K2O)", "氧化钙(CaO)",
    "氧化镁(MgO)", "氧化铝(Al2O3)", "氧化铁(Fe2O3)", "氧化铜(CuO)",
    "氧化铅(PbO)", "氧化钡(BaO)", "五氧化二磷(P2O5)",
    "氧化锶(SrO)", "氧化锡(SnO2)", "二氧化硫(SO2)"
]

# ---------- 日志 ----------
log_lines = []
def log(msg):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{t}] {msg}"
    print(line)
    log_lines.append(line)

# ---------- 读入 ----------
log("读取原始成分表……")
log(f"已成功导入{INPUT_FILE}")
log(f"正在读取表{SHEET_NAME}")
df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)
log(f"原始数据共 {len(df)} 行。")

# ---------- 1. 生成“文物编号”和“采样部位” ----------

def split_sample_point(s: str):
    s = str(s)
    num = ''.join([ch for ch in s if ch.isdigit()])
    part = s.replace(num, '', 1).strip('_')
    return num, part or "Null"

tmp = df["文物采样点"].apply(split_sample_point)
df["文物编号"] = tmp.str[0]
df["采样部位"] = tmp.str[1]
# ---------- 2. 直接复制为质量分数（已是 wt%） ----------
for col in CHEM_COLS:
    df[f"质量分数_{col}"] = pd.to_numeric(df[col], errors="coerce")

mass_cols = [f"{c}" for c in CHEM_COLS]

# ---------- 2‘. 空值为0 ----------
df[mass_cols] = df[mass_cols].fillna(0)

# ---------- 3. 计算累加和 ----------
df["Sum_wt%"] = df[mass_cols].sum(axis=1, min_count=1)

# ---------- 4. 有效性 ----------
df["有效性"] = df["Sum_wt%"].between(85, 105)
invalid = (~df["有效性"]).sum()
log(f"无效行（累加和不在 85–105%）共 {invalid} 行，已剔除。")
df = df[df["有效性"]].copy()

# ---------- 5. 建立主键 ----------
# df["主键"] = df["文物编号"].astype(str) + "_" + df["采样部位"]

# 4. 写 Excel
try:
    os.remove(OUTPUT_FILE)
except FileNotFoundError:
    pass
final_cols = ['文物编号','采样部位','类型','表面风化'] + mass_cols + ['Sum_wt%','有效性']
df_final = df[final_cols]

df_final.to_excel(OUTPUT_FILE, index=False)
log(f"数据清洗结果已保存至 {OUTPUT_FILE}")

# 5. 写日志
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))
log("The log is Saved")

