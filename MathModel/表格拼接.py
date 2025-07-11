
import pandas as pd
from pathlib import Path

# ---------- 路径配置 ----------
RAW_DIR    = Path(r"C:\Users\26790\Desktop\表格数据拼接")
RESULT_DIR = Path(r"C:\Users\26790\Desktop\Result\CleanResult")
RESULT_DIR.mkdir(parents=True, exist_ok=True)

LAND_FILE  = RAW_DIR / "附件1.xlsx"   # 地块信息
PLAN_FILE  = RAW_DIR / "附件2.xlsx"   # 种植计划
OUT_FILE   = RESULT_DIR / "附件2_Sheet1_已插入地块面积.xlsx"

# ---------- 主流程 ----------
def main() -> None:
    # 1. 读取数据
    df_land = pd.read_excel(LAND_FILE, sheet_name=0)
    df_plan = pd.read_excel(PLAN_FILE, sheet_name=0)

    # 2. 建立映射：地块名称 -> 地块面积
    area_map = df_land.set_index("地块名称")["地块面积/亩"].to_dict()

    # 3. 插入面积列
    df_plan["地块面积/亩"] = df_plan["种植地块"].map(area_map)

    # 4. 保存结果
    df_plan.to_excel(OUT_FILE, index=False)
    print(f"✅ 已生成：{OUT_FILE}")

if __name__ == "__main__":
    main()