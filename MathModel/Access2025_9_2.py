# -*- coding: utf-8 -*-
"""
种植计划优化数据准备脚本（最终修复版）
- 修复 load_planting_2023 的 self 参数
- 统一列名，避免 KeyError
"""
import re
import json
import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------
# 路径
# ------------------------------------------------------------------
SRC_DIR   = Path(r"C:\Users\26790\Desktop\BoxFilesPic")
RESULT_DIR = Path(r"C:\Users\26790\Desktop\Result\CleanResult")
RESULT_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------
# 列名映射（兼容各种写法）
# ------------------------------------------------------------------
COL_MAP = {
    "作物编号": "crop_id",
    "作物名称": "crop_name",
    "地块类型": "land_type",
    "种植季次": "season",
    "亩产量/斤": "yield_per_mu",
    "亩产量": "yield_per_mu",
    "种植成本/(元/亩)": "cost_per_mu",
    "种植成本": "cost_per_mu",
    "销售单价/（元/亩）": "price_per_kg",
    "销售单价": "price_per_kg",
    "地块名称": "plot_name",
    "地块名": "plot_name",
    "地块面积/亩": "area",
    "预期销售量/斤": "expected_sales",
    "预期销售量": "expected_sales",
    "种植地块": "plot_name",
}

def normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    """统一列名：去空格、去HTML、小写、映射"""
    rename = {}
    for c in df.columns:
        key = re.sub(r"<.*?>", "", str(c))
        key = re.sub(r"\s+", "", key).lower()
        for k, v in COL_MAP.items():
            if re.sub(r"\s+", "", k).lower() == key:
                rename[c] = v
                break
        else:
            rename[c] = re.sub(r"\s+", "_", str(c).strip())
    return df.rename(columns=rename)

# ------------------------------------------------------------------
# 数据类
# ------------------------------------------------------------------
class CropData:
    def __init__(self, crop_id, crop_name, land_type, season,
                 yield_per_mu, cost_per_mu, price_per_kg):
        self.crop_id = int(crop_id)
        self.crop_name = str(crop_name).strip()
        self.land_type = str(land_type).strip()
        self.season = str(season).strip()
        self.yield_per_mu = float(yield_per_mu)
        self.cost_per_mu = float(cost_per_mu)
        self.price_per_kg = float(price_per_kg)

# ------------------------------------------------------------------
# 读取器
# ------------------------------------------------------------------
class DataLoader:
    def __init__(self, src: Path):
        self.src = src

    def _load(self, file: str, sheet: str = "Sheet1") -> pd.DataFrame:
        path = self.src / file
        if not path.exists():
            raise FileNotFoundError(path)
        df = pd.read_excel(path, sheet_name=sheet)
        return normalize_cols(df)

    def load_stats(self):         return self._load("2023年统计的相关数据.xlsx")
    def load_land(self):          return self._load("地块数据.xlsx")
    def load_sales(self):         return self._load("预期销售量.xlsx")
    def load_planting_2023(self): return self._load("2023年的农作物种植情况.xlsx")   # 已加 self

# ------------------------------------------------------------------
# 处理器
# ------------------------------------------------------------------
class DataProcessor:
    def __init__(self):
        self.stats_df = None
        self.land_df  = None
        self.sales_df = None
        self.plant_df = None

        self.stats_map: Dict[tuple, CropData] = {}
        self.expected_sales: Dict[str, float] = {}
        self.land_info: Dict[str, tuple] = {}
        self.initial_2023: Dict[str, Dict[str, str]] = {}

    def read_all(self):
        loader = DataLoader(SRC_DIR)
        self.stats_df = loader.load_stats()
        self.land_df  = loader.load_land()
        self.sales_df = loader.load_sales()
        self.plant_df = loader.load_planting_2023()

    def build_mappings(self):
        # 1. stats_map
        for _, r in self.stats_df.iterrows():
            key = (r["crop_name"], r["land_type"], r["season"])
            self.stats_map[key] = CropData(
                crop_id=r["crop_id"],
                crop_name=r["crop_name"],
                land_type=r["land_type"],
                season=r["season"],
                yield_per_mu=r["yield_per_mu"],
                cost_per_mu=r["cost_per_mu"],
                price_per_kg=r["price_per_kg"]
            )

        # 2. expected_sales
        self.expected_sales = dict(zip(self.sales_df["crop_name"], self.sales_df["expected_sales"]))

        # 3. land_info
        self.land_info = dict(zip(self.land_df["plot_name"],
                                  zip(self.land_df["land_type"], self.land_df["area"])))

        # 4. initial_2023
        for _, r in self.plant_df.iterrows():
            plot = str(r["plot_name"]).strip()
            season = str(r["season"]).strip()
            crop = str(r["crop_name"]).strip()
            self.initial_2023.setdefault(plot, {})[season] = crop

    def save(self):
        self.stats_df.to_csv(RESULT_DIR / "stats_clean.csv", index=False, encoding="utf-8-sig")
        self.land_df.to_csv(RESULT_DIR / "land_clean.csv", index=False, encoding="utf-8-sig")
        self.sales_df.to_csv(RESULT_DIR / "sales_clean.csv", index=False, encoding="utf-8-sig")
        self.plant_df.to_csv(RESULT_DIR / "plant_2023_clean.csv", index=False, encoding="utf-8-sig")

        with open(RESULT_DIR / "initial_2023.json", "w", encoding="utf-8") as f:
            json.dump(self.initial_2023, f, ensure_ascii=False, indent=2)

    def run(self):
        self.read_all()
        self.build_mappings()
        self.save()
        print("✅ 数据清洗完成，结果已保存至：", RESULT_DIR)

# ------------------------------------------------------------------
# 主入口
# ------------------------------------------------------------------
if __name__ == "__main__":
    DataProcessor().run()
    