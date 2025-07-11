import logging
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


# ---------------- 基础配置 ----------------
@dataclass
class PathConfig:
    src_dir: Path                      # 原始数据目录（包含附件.xlsx）
    result_dir: Path                   # 分析结果目录
    clean_dir: Path                    # 清理后的数据目录
    plot_dir: Path                     # 绘图输出目录
    log_dir: Path                      # 日志目录

    def ensure(self):
        for p in [self.src_dir, self.result_dir, self.clean_dir, self.plot_dir, self.log_dir]:
            p.mkdir(parents=True, exist_ok=True)


class LoggerMixin:
    def __init__(self, name: str, log_path: Path):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(fmt)
        if not self.logger.handlers:
            self.logger.addHandler(fh)

    def log(self, msg: str):
        print(msg)
        self.logger.info(msg)


# ---------------- 工具函数 ----------------
def str2floats(cell):
    """将字符串型数值(含孕周 'w' 'w+' 等) 转为 [float, ...] 列表。"""
    if pd.isna(cell):
        return []
    if isinstance(cell, (int, float, np.integer, np.floating)):
        return [float(cell)]
    s = str(cell).strip().replace('＋', '+').replace('W', 'w').replace('周', 'w')
    # 处理 12w+3、12w+6 等
    if 'w+' in s and len(s.split('w+')) == 2:
        try:
            w, d = s.split('w+')
            return [float(w) + float(d) / 7.0]
        except Exception:
            return []
    # 处理 12w
    if s.endswith('w'):
        try:
            return [float(s[:-1])]
        except Exception:
            return []
    # 直接 float
    try:
        return [float(s)]
    except Exception:
        return []


def convert_gestational_week(s):
    """孕周格式转换到小数周。保持字符串列 -> float 列"""
    arr = str2floats(s)
    return np.nan if len(arr) == 0 else float(arr[0])


# ---------------- 数据处理主类 ----------------
class DataCleaner(LoggerMixin):
    def __init__(self,
                 cfg: PathConfig,
                 filename: str = "附件.xlsx",
                 male_sheet: str = "男胎检测数据",
                 female_sheet: str = "女胎检测数据"):
        self.cfg = cfg
        self.cfg.ensure()
        log_path = self.cfg.log_dir / "data_cleaner.log"
        super().__init__("DataCleaner", log_path)

        self.file = self.cfg.src_dir / filename
        self.male_sheet = male_sheet
        self.female_sheet = female_sheet

    # 读取指定sheet（带存在性与sheet名校验）
    def read_sheet(self, sheet_name: str) -> pd.DataFrame:
        if not self.file.exists():
            raise FileNotFoundError(f"未找到Excel文件: {self.file}，请检查 PathConfig.src_dir 和 filename。")
        try:
            df = pd.read_excel(self.file, sheet_name=sheet_name)
        except ValueError as e:
            # 典型：找不到sheet名
            with pd.ExcelFile(self.file) as xls:
                sheets = xls.sheet_names
            raise ValueError(f"读取工作表失败: {e}\nExcel中可用工作表：{sheets}\n"
                             f"请确认存在工作表“{sheet_name}”。")
        self.log(f"[读取] {self.file.name} -> {sheet_name}  shape={df.shape}")
        return df

    # 将“检测孕周”列格式化为小数周
    def format_gw(self, df: pd.DataFrame, gw_col: str = "检测孕周") -> pd.DataFrame:
        if gw_col in df.columns:
            df[gw_col] = df[gw_col].apply(convert_gestational_week)
            self.log(f"[孕周格式化] 列 {gw_col} 完成")
        else:
            self.log(f"[孕周格式化] 未发现列 {gw_col}，跳过")
        return df

    # 对指定列做 Z-score（新增 *_z 列），允许原列是字符串/多值
    def zscore_columns(self, df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
        for col in cols:
            if col not in df.columns:
                self.log(f"[Z-score] 列 {col} 不存在，跳过")
                continue
            # 收集数值
            nums = []
            for cell in df[col].dropna():
                nums.extend(str2floats(cell))
            if len(nums) == 0:
                self.log(f"[Z-score] 列 {col} 无有效数值，跳过")
                continue
            mu, sig = np.mean(nums), np.std(nums, ddof=0)
            if sig == 0:
                self.log(f"[Z-score] 列 {col} 标准差为0，跳过")
                continue

            def _to_z(cell):
                vals = str2floats(cell)
                if not vals:
                    return np.nan
                return " ".join([f"{(v - mu)/sig:.6f}" for v in vals])

            new_col = f"{col}_z"
            df[new_col] = df[col].map(_to_z)
            self.log(f"[Z-score] {col} -> {new_col}")
        return df

    # 删除染色体Z值异常的行（|Z|>=3）
    def drop_outliers_by_chrom_z(self, df: pd.DataFrame,
                                 chrom_cols: List[str]) -> pd.DataFrame:
        cond = pd.Series([False]*len(df), index=df.index)
        for col in chrom_cols:
            if col not in df.columns:
                self.log(f"[异常值] 列 {col} 不存在，跳过")
                continue
            def has_outlier(cell):
                vals = str2floats(cell)
                return any(abs(v) >= 3 for v in vals)

            outlier_mask = df[col].apply(has_outlier)
            self.log(f"[异常值] {col}: 标记 {outlier_mask.sum()} 行 |Z|>=3")
            cond = cond | outlier_mask

        before = len(df)
        df2 = df.loc[~cond].copy()
        self.log(f"[异常值] 共删除 {before - len(df2)} 行；保留 {len(df2)} 行")
        return df2

    # -------------- 新增：盖帽函数 --------------
    def cap_chrom_z_outliers(self, df: pd.DataFrame, chrom_cols: List[str]) -> pd.DataFrame:
        """|Z|>=3 -> NaN，不删行"""
        for col in chrom_cols:
            if col not in df.columns:
                self.log(f"[盖帽] 列 {col} 不存在，跳过")
                continue

            def _cap(cell):
                vals = str2floats(cell)
                if not vals:
                    return np.nan
                capped = [(v if abs(v) < 3 else np.nan) for v in vals]
                return " ".join(f"{v:.6f}" for v in capped) if capped else np.nan

            df[col] = df[col].map(_cap)
            self.log(f"[盖帽] {col} 完成 |Z|>=3 -> NaN")
        return df

    def make_survival_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """男胎→生存格式：一行一个孕妇，time=首次达标孕周，event=1/0"""
        df = df.dropna(subset=['孕妇代码', '检测孕周', 'Y染色体浓度'])
        df = df[(df['Y染色体浓度'] >= 0) & (df['Y染色体浓度'] <= 1)]
        grouped = df.groupby('孕妇代码')
        rows = []
        for pid, g in grouped:
            g = g.sort_values('检测孕周')
            达标记录 = g[g['Y染色体浓度'] >= 0.04]
            if 达标记录.empty:
                T = g['检测孕周'].iloc[-1]
                E = 0
            else:
                T = 达标记录.iloc[0]['检测孕周']
                E = 1
            first = g.iloc[0]
            rows.append({
                'patient_id': pid,
                'time': T,
                'event': E,
                'bmi': first['孕妇BMI'],
                'age': first['年龄'],
                'weight': first['体重'],
                'parity': first['生产次数'],
                'mean_filtered_ratio': g['被过滤掉读段数的比例'].mean()
            })
        return pd.DataFrame(rows)


    # 保存清洗结果
    def save_cleaned(self, df: pd.DataFrame, gender: str, name: str):
        out_dir = self.cfg.clean_dir / gender
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / name
        df.to_excel(path, index=False)
        self.log(f"[保存清洗] {path}")

    # 处理单个 sheet
    def process_one(self,
                    sheet_name: str,
                    zscore_cols: List[str],
                    chrom_z_cols: List[str]) -> pd.DataFrame:
        df = self.read_sheet(sheet_name)
        df = self.format_gw(df, "检测孕周")
        df = self.zscore_columns(df, zscore_cols)
        df = self.cap_chrom_z_outliers(df, chrom_z_cols)
        gender = "男胎" if "男" in sheet_name else "女胎"
        self.save_cleaned(df, gender, f"{sheet_name}_cleaned.xlsx")
        return df
        if "男" in sheet_name:
            survival_df = self.make_survival_data(df)
            out_csv = self.cfg.clean_dir / '男胎' / 'cleaned_survival_data.csv'
            survival_df.to_csv(out_csv, index=False)
            self.log(f"[生存数据] 已生成 {out_csv} 形状={survival_df.shape}")

    # 同时处理男女胎
    def run_all(self,
                zscore_cols: List[str],
                chrom_z_cols: List[str]) -> Dict[str, pd.DataFrame]:
        out = {}
        for sheet in [self.male_sheet, self.female_sheet]:
            out[sheet] = self.process_one(sheet, zscore_cols, chrom_z_cols)
        return out
