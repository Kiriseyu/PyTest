import logging
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


# ---------- Paths ----------
@dataclass
class PathConfig:
    src_dir: Path      # directory containing 附件.xlsx
    result_dir: Path   # analysis outputs
    clean_dir: Path    # cleaned data outputs
    plot_dir: Path     # figures
    log_dir: Path      # logs

    def ensure(self):
        for p in [self.src_dir, self.result_dir, self.clean_dir, self.plot_dir, self.log_dir]:
            p.mkdir(parents=True, exist_ok=True)


# ---------- Logger ----------
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


# ---------- Helpers ----------
def str2floats(cell):
    """Parse a cell that might contain values like '12w+3', '12w', '12', '12.5'.
    Returns a list[float]."""
    if pd.isna(cell):
        return []
    if isinstance(cell, (int, float, np.integer, np.floating)):
        return [float(cell)]
    s = str(cell).strip().replace('＋', '+').replace('W', 'w').replace('周', 'w')
    # 12w+3
    if 'w+' in s and len(s.split('w+')) == 2:
        try:
            w, d = s.split('w+')
            return [float(w) + float(d) / 7.0]
        except Exception:
            return []
    # 12w
    if s.endswith('w'):
        try:
            return [float(s[:-1])]
        except Exception:
            return []
    # space-separated numbers or plain number
    try:
        return [float(x) for x in s.split()]
    except Exception:
        return []


def convert_gestational_week(cell) -> float:
    arr = str2floats(cell)
    return np.nan if len(arr) == 0 else float(arr[0])


# ---------- Data Cleaner ----------
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

    def read_sheet(self, sheet_name: str) -> pd.DataFrame:
        if not self.file.exists():
            raise FileNotFoundError(f"未找到Excel文件: {self.file}，请检查 PathConfig.src_dir 和 filename。")
        try:
            df = pd.read_excel(self.file, sheet_name=sheet_name)
        except ValueError as e:
            with pd.ExcelFile(self.file) as xls:
                sheets = xls.sheet_names
            raise ValueError(f"读取工作表失败: {e}\n可用工作表：{sheets}")
        self.log(f"[读取] {self.file.name} -> {sheet_name}  shape={df.shape}")
        return df

    def format_gw(self, df: pd.DataFrame, gw_col: str = "检测孕周") -> pd.DataFrame:
        if gw_col in df.columns:
            df[gw_col] = df[gw_col].apply(convert_gestational_week)
            self.log(f"[孕周格式化] 列 {gw_col} 完成")
        else:
            self.log(f"[孕周格式化] 未发现列 {gw_col}，跳过")
        return df

    def zscore_columns(self, df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
        """Add numeric *_z columns (single float per row). For multi-parsed values, take the first."""
        for col in cols:
            if col not in df.columns:
                self.log(f"[Z-score] 列 {col} 不存在，跳过")
                continue
            vals = df[col].apply(lambda x: (str2floats(x)[0] if len(str2floats(x)) else np.nan))
            mu = vals.mean(skipna=True)
            sig = vals.std(skipna=True, ddof=0)
            if not np.isfinite(sig) or sig == 0:
                self.log(f"[Z-score] 列 {col} 标准差为0或无效，跳过")
                continue
            df[f"{col}_z"] = (vals - mu) / sig
            self.log(f"[Z-score] {col} -> {col}_z")
        return df

    def cap_chrom_z_outliers(self, df: pd.DataFrame, chrom_cols: List[str]) -> pd.DataFrame:
        """For chromosomal Z columns (already Z-score by definition), set |Z|>=3 to NaN; do not drop rows."""
        for col in chrom_cols:
            if col not in df.columns:
                self.log(f"[盖帽] 列 {col} 不存在，跳过")
                continue
            def _cap(cell):
                arr = str2floats(cell)
                if not arr:
                    return np.nan
                v = arr[0]
                return v if abs(v) < 3 else np.nan
            df[col] = df[col].apply(_cap)
            self.log(f"[盖帽] {col} 完成 |Z|>=3 -> NaN")
        return df

    def make_survival_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """One row per patient. time = earliest week reaching Y>=0.04, event=1 if reached else 0."""
        req = ['孕妇代码', '检测孕周', 'Y染色体浓度', '孕妇BMI', '年龄', '体重', '生产次数', '被过滤掉读段数的比例']
        for col in req:
            if col not in df.columns:
                df[col] = np.nan
        df = df.dropna(subset=['孕妇代码', '检测孕周', 'Y染色体浓度'])
        # assume Y in [0,1] (if given as percent ~0.04, values already <=1 in附件)
        grouped = df.groupby('孕妇代码')
        rows = []
        for pid, g in grouped:
            g = g.sort_values('检测孕周')
            reached = g[g['Y染色体浓度'] >= 0.04]
            if reached.empty:
                T, E = g['检测孕周'].iloc[-1], 0
            else:
                T, E = reached.iloc[0]['检测孕周'], 1
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

    def save_cleaned(self, df: pd.DataFrame, gender: str, name: str):
        out_dir = self.cfg.clean_dir / gender
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / name
        df.to_excel(path, index=False)
        self.log(f"[保存清洗] {path}")

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
        # ---- generate survival data for male before returning ----
        if "男" in sheet_name:
            survival_df = self.make_survival_data(df)
            out_csv = self.cfg.clean_dir / '男胎' / 'cleaned_survival_data.csv'
            survival_df.to_csv(out_csv, index=False)
            self.log(f"[生存数据] 已生成 {out_csv} 形状={survival_df.shape}")
        return df

    def run_all(self,
                zscore_cols: List[str],
                chrom_z_cols: List[str]) -> Dict[str, pd.DataFrame]:
        out = {}
        for sheet in [self.male_sheet, self.female_sheet]:
            out[sheet] = self.process_one(sheet, zscore_cols, chrom_z_cols)
        return out
