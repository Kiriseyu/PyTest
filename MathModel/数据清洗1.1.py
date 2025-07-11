import os
import pandas as pd
from datetime import datetime

# ---------- 0. 基础配置 ----------
WB1_FILE   = os.path.join( r"C:/Users/26790/Desktop/Cleaned/工作簿1.xlsx")
FORM1_FILE = os.path.join( r"C:/Users/26790/Desktop/Cleaned/表单1.xlsx")
OUT_DIR    = os.path.join( "./result")
os.makedirs(OUT_DIR, exist_ok=True)

CLEANED    = os.path.join(OUT_DIR, "cleaned.xlsx")
MERGED     = os.path.join(OUT_DIR, "merged.xlsx")
LOG_PATH   = os.path.join(OUT_DIR, "clean.log")

CHEM_COLS = [
    "二氧化硅(SiO2)", "氧化钠(Na2O)", "氧化钾(K2O)", "氧化钙(CaO)",
    "氧化镁(MgO)", "氧化铝(Al2O3)", "氧化铁(Fe2O3)", "氧化铜(CuO)",
    "氧化铅(PbO)", "氧化钡(BaO)", "五氧化二磷(P2O5)",
    "氧化锶(SrO)", "氧化锡(SnO2)", "二氧化硫(SO2)"
]

# ---------- Log ----------
log_lines = []
def log(msg):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{t}] {msg}"
    print(line)
    log_lines.append(line)

# ---------- 1. 读入 ----------
log("开始读取原始成分表……")
df = pd.read_excel(WB1_FILE, sheet_name="Sheet1")
log(f"原始数据共 {len(df)} 行")

def split_sample_point(s: str):
    s = str(s)
    num = ''.join(ch for ch in s if ch.isdigit())
    part = s.replace(num, '', 1).strip('_')
    return num.zfill(2), part or "Null"

tmp = df["文物采样点"].apply(split_sample_point)
df["文物编号"] = tmp.str[0]
df["采样部位"] = tmp.str[1]

# ---------- 3. 质量分数列（空值→0） ----------
for col in CHEM_COLS:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# ---------- 4. 累加和有效性 ----------
df["Sum_wt%"] = df[CHEM_COLS].sum(axis=1)
df["有效性"]  = df["Sum_wt%"].between(85, 105)
invalid = (~df["有效性"]).sum()
log(f"无效行（累加和不在 85–105%）共 {invalid} 行，已剔除")
df = df[df["有效性"]].copy()

# ---------- 5. 保存清洗结果 ----------
final_cols = ["文物编号", "采样部位", "类型", "表面风化"] + CHEM_COLS + ["Sum_wt%", "有效性"]
df_final = df[final_cols].copy()          # 关键：消除 SettingWithCopyWarning
df_final.to_excel(CLEANED, index=False)
log(f"清洗结果已保存至 {CLEANED}")

# ---------- 6. 合并表单 1：纹饰 / 颜色 ----------
if not os.path.exists(FORM1_FILE):
    log("⚠️ 表单1.xlsx 未找到，跳过合并纹饰/颜色")
else:
    form1 = (
        pd.read_excel(FORM1_FILE, sheet_name=0, dtype={"文物编号": str})
          .loc[:, ["文物编号", "纹饰", "颜色"]]
          .assign(文物编号=lambda x: x["文物编号"].str.zfill(2))
    )
    df_merged = (
        df_final
        .merge(form1, on="文物编号", how="left")
        [["文物编号", "纹饰", "颜色"] + [c for c in df_final.columns if c != "文物编号"]]
    )
    df_merged.to_excel(MERGED, index=False)
    log(f"已把纹饰/颜色并入，结果保存至 {MERGED}")

# ---------- 7. 写日志 ----------
with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))
log("全部完成！")