# This script creates four Python files implementing the user's requested OOP pipeline.
# Files:
# - 数据处理.py
# - 绘图.py
# - 建模分析.py
# - main.py
#
# They follow the directory structure and behavior specified by the user.

from pathlib import Path

root = Path("/mnt/data")
root.mkdir(parents=True, exist_ok=True)

# ---------------- 数据处理.py ----------------
data_processing_code = r'''# -*- coding: utf-8 -*-
"""
数据处理.py
-----------------
负责：
1) 读取 Excel（男女胎两个 sheet）
2) 孕周格式标准化（如 "12w+3" -> 12 + 3/7）
3) 选定列的 Z-score 标准化
4) 13/18/21/X/Y 染色体Z值异常（|Z|>=3）行删除
5) 保存清洗结果与日志

输出：
- 清洗后数据另存至 CleanResult/男女胎/xxx.xlsx
- 日志输出至 CleanedLog
"""

import os
import re
import logging
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional

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

    # 读取指定sheet
    def read_sheet(self, sheet_name: str) -> pd.DataFrame:
        df = pd.read_excel(self.file, sheet_name=sheet_name)
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

    # 对指定列做 Z-score（新增 *_z 列；若列含'空格分隔'的字符串，则对解析后每个值做z并拼回空格串）
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

    # 对 13/18/21/X/Y 染色体Z值 列(|Z|>=3)做异常值删除（整行）
    def drop_outliers_by_chrom_z(self, df: pd.DataFrame,
                                 chrom_cols: List[str]) -> pd.DataFrame:
        cond = pd.Series([False]*len(df), index=df.index)
        for col in chrom_cols:
            if col not in df.columns:
                self.log(f"[异常值] 列 {col} 不存在，跳过")
                continue
            # 列可能是数值或字符串（空格分隔多个值）
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

    # 保存到 CleanResult/男女胎 子目录
    def save_cleaned(self, df: pd.DataFrame, gender: str, name: str):
        out_dir = self.cfg.clean_dir / gender
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / name
        df.to_excel(path, index=False)
        self.log(f"[保存清洗] {path}")

    # 主流程（针对一个 sheet）
    def process_one(self,
                    sheet_name: str,
                    zscore_cols: List[str],
                    chrom_z_cols: List[str]) -> pd.DataFrame:
        df = self.read_sheet(sheet_name)
        df = self.format_gw(df, "检测孕周")
        df = self.zscore_columns(df, zscore_cols)
        df = self.drop_outliers_by_chrom_z(df, chrom_z_cols)
        gender = "男胎" if "男" in sheet_name else "女胎"
        self.save_cleaned(df, gender, f"{sheet_name}_cleaned.xlsx")
        return df

    # 两个 sheet 一起跑
    def run_all(self,
                zscore_cols: List[str],
                chrom_z_cols: List[str]) -> Dict[str, pd.DataFrame]:
        out = {}
        for sheet in [self.male_sheet, self.female_sheet]:
            out[sheet] = self.process_one(sheet, zscore_cols, chrom_z_cols)
        return out
'''

# ---------------- 绘图.py ----------------
plotting_code = r'''# -*- coding: utf-8 -*-
"""
绘图.py
-----------------
负责：
1) 统一中文、负号显示参数
2) 可开关的绘图（直方图、Q-Q图、热力图等）
3) 男女胎各自独立文件夹写入

输出：Plotting/男胎|女胎/*.png
"""

import os
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore")


@dataclass
class PlotConfig:
    enable: bool
    base_dir: Path

    def gender_dir(self, gender: str) -> Path:
        d = self.base_dir / gender
        d.mkdir(parents=True, exist_ok=True)
        return d


def setup_chinese():
    plt.rcParams['axes.unicode_minus'] = False
    try:
        plt.rcParams['font.family'] = 'SimHei'
    except Exception:
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']


class Plotter:
    def __init__(self, cfg: PlotConfig):
        self.cfg = cfg
        setup_chinese()

    def _maybe_save(self, fig, path: Path):
        if not self.cfg.enable:
            plt.close(fig)
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=300, bbox_inches='tight')
        plt.close(fig)

    def hist_and_qq(self, df: pd.DataFrame, col: str, gender: str):
        if col not in df.columns:
            return
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if series.empty:
            return
        fig = plt.figure(figsize=(10,4))
        ax1 = fig.add_subplot(1,2,1)
        sns.histplot(series, kde=True, ax=ax1)
        ax1.set_title(f"{col} 直方图")
        ax2 = fig.add_subplot(1,2,2)
        stats.probplot(series, dist="norm", plot=ax2)
        ax2.set_title(f"{col} Q-Q 图")
        out = self.cfg.gender_dir(gender) / f"{col}_hist_qq.png"
        self._maybe_save(fig, out)

    def heatmap(self, corr: pd.DataFrame, name: str, gender: str, cmap="coolwarm"):
        fig = plt.figure(figsize=(8,6))
        ax = fig.add_subplot(1,1,1)
        sns.heatmap(corr, annot=True, fmt=".2f", cmap=cmap, ax=ax)
        ax.set_title(f"{name} 相关系数矩阵")
        out = self.cfg.gender_dir(gender) / f"{name}_corr_heatmap.png"
        self._maybe_save(fig, out)
'''

# ---------------- 建模分析.py ----------------
analysis_code = r'''# -*- coding: utf-8 -*-
"""
建模分析.py
-----------------
负责：
1) 描述统计、正态性检验（含QQ图）
2) 多重共线性（VIF）
3) 皮尔逊相关矩阵
4) 多元线性回归（含F检验/T检验，系数表、残差QQ图）
5) 线性混合模型（groups=孕妇代码），残差QQ图
6) 结果写出至 AnalysisResult

说明：QQ图、热力图等调用 绘图.Plotter
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.formula.api import ols, mixedlm

from 绘图 import Plotter, PlotConfig


@dataclass
class AnalysisConfig:
    result_dir: Path
    plotter: Plotter

    def ensure(self):
        self.result_dir.mkdir(parents=True, exist_ok=True)


class Analyzer:
    def __init__(self, cfg: AnalysisConfig, logger: logging.Logger):
        self.cfg = cfg
        self.cfg.ensure()
        self.logger = logger

    def log(self, msg: str):
        print(msg)
        self.logger.info(msg)

    # -------- 描述统计 --------
    def descriptive(self, df: pd.DataFrame, gender: str) -> pd.DataFrame:
        num = df.select_dtypes(include=np.number).dropna(axis=1, how='all')
        num = num.loc[:, num.nunique() > 1]
        desc = num.describe().T
        desc["偏度"] = num.skew()
        desc["峰度"] = num.kurt()
        out = self.cfg.result_dir / f"{gender}_描述性统计.xlsx"
        desc.to_excel(out)
        self.log(f"[描述统计] {gender} -> {out}")
        return desc

    # -------- 正态性检验 + QQ图 --------
    def normality(self, df: pd.DataFrame, cols: List[str], gender: str):
        for col in cols:
            if col not in df.columns:
                self.log(f"[正态性] {gender} 列 {col} 不存在，跳过")
                continue
            series = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(series) < 8:
                self.log(f"[正态性] {gender} 列 {col} 有效样本不足(<8)，跳过")
                continue
            if len(series) <= 5000:
                W, p = stats.shapiro(series)
            else:
                from statsmodels.stats.diagnostic import lilliefors
                W, p = lilliefors(series)
            self.log(f"[正态性] {gender} {col}: W={W:.6f} p={p:.6f} 正态={'是' if p>0.05 else '否'}")
            # QQ图
            self.cfg.plotter.hist_and_qq(df, col, gender)

    # -------- 多重共线性 VIF --------
    def vif(self, df: pd.DataFrame, cols: List[str], gender: str):
        X = df[cols].apply(pd.to_numeric, errors="coerce").dropna()
        if X.empty or X.shape[1] < 2:
            self.log(f"[VIF] {gender} 无足够数值列，跳过")
            return
        vif_df = pd.DataFrame({
            "feature": X.columns,
            "VIF": [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
        })
        out = self.cfg.result_dir / f"{gender}_VIF.xlsx"
        vif_df.to_excel(out, index=False)
        self.log(f"[VIF] {gender} -> {out}")

    # -------- 皮尔逊相关 --------
    def pearson_corr(self, df: pd.DataFrame, gender: str):
        num = df.select_dtypes(include=np.number).dropna(axis=1, how='all')
        num = num.loc[:, num.nunique() > 1]
        if num.shape[1] < 2:
            self.log(f"[相关矩阵] {gender} 数值列不足，跳过")
            return
        corr = num.corr(method="pearson")
        out = self.cfg.result_dir / f"{gender}_相关矩阵.xlsx"
        corr.to_excel(out)
        self.log(f"[相关矩阵] {gender} -> {out}")
        # 热力图
        self.cfg.plotter.heatmap(corr.round(2), f"{gender}", gender)

    # -------- 多元线性回归 --------
    def linear_regression(self, df: pd.DataFrame, y: str, X_cols: List[str], gender: str):
        data = df[X_cols + [y]].apply(pd.to_numeric, errors="coerce").dropna()
        if data.empty:
            self.log(f"[线性回归] {gender} 数据为空，跳过")
            return
        X = sm.add_constant(data[X_cols])
        model = sm.OLS(data[y], X).fit()
        # 保存系数与显著性
        coef = model.params.to_frame("Coef")
        coef["t"] = model.tvalues
        coef["P>|t|"] = model.pvalues
        out_coef = self.cfg.result_dir / f"{gender}_线性回归_系数.xlsx"
        coef.to_excel(out_coef)
        # 保存整体摘要（包含F检验、R2等）
        out_txt = self.cfg.result_dir / f"{gender}_线性回归_摘要.txt"
        with open(out_txt, "w", encoding="utf-8") as f:
            f.write(model.summary().as_text())
        self.log(f"[线性回归] {gender} 完成 -> {out_coef} | {out_txt}")
        # 残差QQ图
        resid = model.resid
        tmp = data.copy()
        tmp["__resid__"] = resid
        self.cfg.plotter.hist_and_qq(tmp, "__resid__", gender)

    # -------- 线性混合模型 --------
    def mixed_model(self, df: pd.DataFrame, formula: str, group_col: str, gender: str):
        if group_col not in df.columns:
            self.log(f"[混合模型] {gender} 分组列 {group_col} 不存在，跳过")
            return
        data = df.copy()
        # 保证参与建模列为数值/可解释
        # 让 patsy 自动处理，但先去掉明显的非数值空值
        data = data.dropna(subset=[group_col])
        try:
            model = mixedlm(formula, data=data, groups=data[group_col])
            result = model.fit(maxiter=500)
        except Exception as e:
            self.log(f"[混合模型] {gender} 拟合失败：{e}")
            return
        # 保存固定效应
        fe = result.fe_params.round(6).to_frame("FixedEffect")
        out_fe = self.cfg.result_dir / f"{gender}_混合模型_固定效应.xlsx"
        fe.to_excel(out_fe)
        # 保存摘要
        out_txt = self.cfg.result_dir / f"{gender}_混合模型_摘要.txt"
        with open(out_txt, "w", encoding="utf-8") as f:
            f.write(str(result.summary()))
        self.log(f"[混合模型] {gender} 完成 -> {out_fe} | {out_txt}")
        # 残差QQ图
        resid = pd.Series(result.resid).dropna()
        tmp = pd.DataFrame({"__resid__": resid})
        self.cfg.plotter.hist_and_qq(tmp, "__resid__", gender)
'''

# ---------------- main.py ----------------
main_code = r'''# -*- coding: utf-8 -*-
"""
main.py
-----------------
一站式调度器：
- 读取 C:\Users\26790\Desktop\BoxFilesPic\附件.xlsx
- 清洗（孕周格式化、Z-score、异常值剔除）
- 正态性/VIF/相关/线性回归/线性混合回归
- 绘图统一开关；绘图输出到 Plotting/男胎|女胎
- 结果输出到 Result/AnalysisResult，清洗数据到 Result/CleanResult
- 日志到 CleanedLog

运行：
    python main.py
"""

import logging
from pathlib import Path

from 数据处理 import PathConfig, DataCleaner
from 绘图 import PlotConfig, Plotter
from 建模分析 import AnalysisConfig, Analyzer

# ---------------- 路径配置（按用户要求） ----------------
SRC_DIR = Path(r"C:\Users\26790\Desktop\BoxFilesPic")
ANALYSIS_DIR = Path(r"C:\Users\26790\Desktop\Result\AnalysisResult")
CLEAN_DIR = Path(r"C:\Users\26790\Desktop\Result\CleanResult")
PLOT_DIR = Path(r"C:\Users\26790\Desktop\Result\Plotting")
LOG_DIR = Path(r"C:\Users\26790\Desktop\CleanedLog")

# ---------------- 日志器 ----------------
LOG_DIR.mkdir(parents=True, exist_ok=True)
main_log_file = LOG_DIR / "main.log"
logging.basicConfig(filename=main_log_file, filemode="a", encoding="utf-8",
                    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Main")

# ---------------- 绘图开关 ----------------
ENABLE_PLOTS = True   # 需要可切换 True/False

plotter = Plotter(PlotConfig(enable=ENABLE_PLOTS, base_dir=PLOT_DIR))

# ---------------- 数据清洗 ----------------
cfg = PathConfig(src_dir=SRC_DIR, result_dir=ANALYSIS_DIR, clean_dir=CLEAN_DIR, plot_dir=PLOT_DIR, log_dir=LOG_DIR)
cleaner = DataCleaner(cfg)

# 需要Z-score的列
ZSCORE_COLS = ["检测孕周", "孕妇BMI", "年龄", "生产次数"]
# 需要根据|Z|>=3剔除整行的染色体Z值列名（需与表头一致）
CHROM_Z_COLS = ["13染色体的Z值", "18染色体的Z值", "21染色体的Z值", "X染色体的Z值", "Y染色体的Z值"]

data_by_sheet = cleaner.run_all(ZSCORE_COLS, CHROM_Z_COLS)

# ---------------- 建模分析 ----------------
analysis_cfg = AnalysisConfig(result_dir=ANALYSIS_DIR, plotter=plotter)
analyzer = Analyzer(analysis_cfg, logger)

# 要进行正态性检验的列
NORMAL_COLS = ["年龄", "孕妇BMI", "检测孕周", "Y染色体浓度"]

# 多元线性回归设定：Y = β1*检测孕周 + β2*孕妇BMI + β3*年龄 + ε
Y_COL = "Y染色体浓度"
X_COLS = ["检测孕周", "孕妇BMI", "年龄"]

for sheet_name, df in data_by_sheet.items():
    gender = "男胎" if "男" in sheet_name else "女胎"

    # 描述统计
    analyzer.descriptive(df, gender)

    # 正态性 + QQ图
    analyzer.normality(df, NORMAL_COLS, gender)

    # 多重共线性（VIF）
    analyzer.vif(df, X_COLS + ["生产次数"], gender)

    # 皮尔逊相关
    analyzer.pearson_corr(df, gender)

    # 多元线性回归（含F/T/残差QQ图）
    analyzer.linear_regression(df, Y_COL, X_COLS, gender)

    # 线性混合模型（示例：与用户一致）
    analyzer.mixed_model(df, formula=f"{Y_COL} ~ 检测孕周 + 孕妇BMI", group_col="孕妇代码", gender=gender)

print(">>> 全部任务完成！输出：")
print(f"清洗数据 -> {CLEAN_DIR}")
print(f"分析结果 -> {ANALYSIS_DIR}")
print(f"绘图结果 -> {PLOT_DIR}")
print(f"日志 -> {LOG_DIR}")
'''

# Write files
(files := {
    "数据处理.py": data_processing_code,
    "绘图.py": plotting_code,
    "建模分析.py": analysis_code,
    "main.py": main_code,
})

for name, content in files.items():
    (root / name).write_text(content, encoding="utf-8")

[str(root / name) for name in files.keys()]

['/mnt/data/数据处理.py',
 '/mnt/data/绘图.py',
 '/mnt/data/建模分析.py',
 '/mnt/data/main.py']