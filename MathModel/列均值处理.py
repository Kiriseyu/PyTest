import os
import re
import pandas as pd

# ---------- 1. 路径 ----------
SRC_DIR   = r"C:\Users\26790\Desktop\BoxFilesPic"
DST_DIR   = r"C:\Users\26790\Desktop\Result\CleanResult"
os.makedirs(DST_DIR, exist_ok=True)

SRC_FILE  = os.path.join(SRC_DIR, "附件2.xlsx")
DST_FILE  = os.path.join(DST_DIR, "CleanResult.xlsx")

# ---------- 2. 读 ----------
df = pd.read_excel(SRC_FILE, sheet_name="2023年统计的相关数据")

# ---------- 3. 区间均值函数 ----------
def parse_range_avg(text):
    if pd.isna(text):
        return text
    text = str(text).strip()
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", text)
    if m:
        return (float(m.group(1)) + float(m.group(2))) / 2
    try:
        return float(text)
    except ValueError:
        return text

# ---------- 4. 处理 ----------
price_col_name = "销售单价/(元/斤)"
if price_col_name not in df.columns:
    raise ValueError(f"未找到列【{price_col_name}】，请检查列名或工作表是否正确")

df["销售单价_区间均值(元/斤)"] = df[price_col_name].apply(parse_range_avg)

# ---------- 5. 保存 ----------
df.to_excel(DST_FILE, sheet_name="Sheet2", index=False)
print("处理完毕，结果已保存至：", DST_FILE)