from __future__ import annotations
import logging
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import (
    roc_auc_score, confusion_matrix,
    RocCurveDisplay, PrecisionRecallDisplay, precision_recall_curve
)
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils import resample
from lifelines import CoxPHFitter, KaplanMeierFitter

warnings.filterwarnings('ignore')
PathLike = Union[str, Path]

# ================= PathConfig =================
@dataclass
class PathConfig:
    src_dir: Path
    kk_dr: Path
    sr_dr: Path
    zu_dr: Path
    log_dir: Path

    @property
    def result_dir(self):
        return self.kk_dr
    @property
    def clean_dir(self):
        return self.sr_dr
    @property
    def plot_dir(self):
        return self.zu_dr

    def ensure(self):
        for keiro in [self.src_dir, self.kk_dr, self.sr_dr, self.zu_dr, self.log_dir]:
            keiro.mkdir(parents=True, exist_ok=True)

# ================= Logger =================
class LoggerMixin:
    def __init__(self, namae: str, log_keiro: Path):
        self.logger = logging.getLogger(namae)
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler(log_keiro, encoding='utf-8')
        fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(fmt)
        if not self.logger.handlers:
            self.logger.addHandler(fh)

    def log(self, mes: str):
        print(mes)
        self.logger.info(mes)

# ================= Utils =================
def _to_float_list(seru) -> List[float]:
    if pd.isna(seru):
        return []
    if isinstance(seru, (int, float, np.integer, np.floating)):
        return [float(seru)]
    bun = str(seru).strip().replace('＋', '+').replace('W', 'w').replace('周', 'w')
    if 'w+' in bun and len(bun.split('w+')) == 2:
        try:
            w, d = bun.split('w+')
            return [float(w) + float(d) / 7.0]
        except Exception:
            return []
    if bun.endswith('w'):
        try:
            return [float(bun[:-1])]
        except Exception:
            return []
    try:
        return [float(x) for x in bun.split()]
    except Exception:
        return []

def to_gw_float(seru) -> float:
    arr = _to_float_list(seru)
    return np.nan if not arr else float(arr[0])

def setup_chinese():
    plt.rcParams['axes.unicode_minus'] = False
    try:
        plt.rcParams['font.family'] = 'SimHei'
    except Exception:
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

# ================= DataCleaner =================
class DataCleaner(LoggerMixin):
    def __init__(self, settei: PathConfig, 文件名: str='附件.xlsx', 男胎表: str='男胎检测数据', 女胎表: str='女胎检测数据'):
        self.cfg = settei
        self.cfg.ensure()
        super().__init__('DataCleaner', self.cfg.log_dir / 'data_cleaner.log')
        self.file = self.cfg.src_dir / 文件名
        self.male_sheet = 男胎表
        self.female_sheet = 女胎表

    def yomu_sheet(self, sheet_mei: str) -> pd.DataFrame:
        if not self.file.exists():
            raise FileNotFoundError(f'未找到Excel文件: {self.file}')
        try:
            df = pd.read_excel(self.file, sheet_name=sheet_mei)
        except ValueError as e:
            with pd.ExcelFile(self.file) as xls:
                mee = xls.sheet_names
            raise ValueError(f'读取工作表失败: {e}\n可用工作表：{mee}')
        self.log(f'[读取] {self.file.name} -> {sheet_mei}  shape={df.shape}')
        return df

    def missing_value_heatmap(self, df: pd.DataFrame, output_path: Path):
        plt.figure(figsize=(12, 8))
        sns.heatmap(df.isnull(), cbar=False, cmap='viridis', yticklabels=False)
        plt.title('缺失值热力图', fontproperties='SimHei')
        plt.savefig(output_path, dpi=300)
        plt.close()
        self.log(f'[热力图] 缺失值热力图已保存 -> {output_path}')

    def seiri_ninshu(self, df: pd.DataFrame, ninshu_col: str='检测孕周') -> pd.DataFrame:
        if ninshu_col in df.columns:
            df[ninshu_col] = df[ninshu_col].apply(to_gw_float)
            self.log(f'[孕周格式化] 列 {ninshu_col} 完成（→ 浮点周）')
        else:
            self.log(f'[孕周格式化] 未发现列 {ninshu_col}，跳过')
        return df

    def keisoku_zscore(self, df: pd.DataFrame, retsu: List[str]) -> pd.DataFrame:
        for col in retsu:
            if col not in df.columns:
                self.log(f'[Z-score] 列 {col} 不存在，跳过')
                continue
            kazu = []
            for seru in df[col].dropna():
                kazu.extend(_to_float_list(seru))
            if not kazu:
                self.log(f'[Z-score] 列 {col} 无有效数值，跳过')
                continue
            mu, sig = (np.mean(kazu), np.std(kazu, ddof=0))
            if sig == 0:
                self.log(f'[Z-score] 列 {col} 标准差为0，跳过')
                continue
            df[f'{col}_z'] = df[col].map(
                lambda c: np.nan if not _to_float_list(c) else (_to_float_list(c)[0] - mu) / sig
            )
            self.log(f'[Z-score] {col} -> {col}_z（数值列）')
        return df

    def cap_chrm_z(self, df: pd.DataFrame, kromu_retsu: List[str]) -> pd.DataFrame:
        for col in kromu_retsu:
            if col not in df.columns:
                self.log(f'[盖帽] 列 {col} 不存在，跳过')
                continue
            def _cap(seru):
                arr = _to_float_list(seru)
                if not arr:
                    return np.nan
                v = arr[0]
                return v if np.isfinite(v) and abs(v) < 3 else np.nan
            df[col] = df[col].map(_cap)
            self.log(f'[盖帽] {col} 完成 |Z|>=3 -> NaN')
        return df

    def sakusei_seizon(self, df: pd.DataFrame) -> pd.DataFrame:
        hitsuyou = ['孕妇代码', '检测孕周', 'Y染色体浓度', '孕妇BMI', '年龄', '体重', '生产次数']
        for c in hitsuyou:
            if c not in df.columns:
                df[c] = np.nan
        df = df.dropna(subset=['孕妇代码', '检测孕周', 'Y染色体浓度'])
        df = df[(df['Y染色体浓度'] >= 0) & (df['Y染色体浓度'] <= 1)]
        gyou = []
        for pid, g in df.groupby('孕妇代码', sort=False):
            g = g.sort_values('检测孕周')
            atari = g[g['Y染色体浓度'] >= 0.04]
            if atari.empty:
                T, E = (g['检测孕周'].iloc[-1], 0)
            else:
                T, E = (atari.iloc[0]['检测孕周'], 1)
            b = g.iloc[0]
            gyou.append({
                'patient_id': pid, 'time': float(T), 'event': int(E),
                'bmi': float(b.get('孕妇BMI', np.nan)), 'age': float(b.get('年龄', np.nan)),
                'weight': float(b.get('体重', np.nan)), 'parity': float(b.get('生产次数', np.nan))
            })
        return pd.DataFrame(gyou)
    def hozon_seiri(self, df: pd.DataFrame, seibetsu: str, namae: str):
        sy_dr = self.cfg.clean_dir / seibetsu
        sy_dr.mkdir(parents=True, exist_ok=True)
        keiro = sy_dr / namae
        df.to_excel(keiro, index=False)
        self.log(f'[保存清洗] {keiro}')

    def shori_ichibu(self, sheet_mei: str, zscore_retsu: List[str], kromu_z_retsu: List[str]) -> pd.DataFrame:
        df = self.yomu_sheet(sheet_mei)
        df = self.seiri_ninshu(df, '检测孕周')
        df = self.keisoku_zscore(df, zscore_retsu)
        df = self.cap_chrm_z(df, kromu_z_retsu)
        seibetsu = '男胎' if '男' in sheet_mei else '女胎'
        self.hozon_seiri(df, seibetsu, f'{sheet_mei}_cleaned.xlsx')
        if '男' in sheet_mei:
            df_sz = self.sakusei_seizon(df)
            out_csv = self.cfg.clean_dir / '男胎' / 'cleaned_survival_data.csv'
            df_sz.to_csv(out_csv, index=False)
            self.log(f'[生存数据] 已生成 {out_csv} 形状={df_sz.shape}')
        return df

    def jikkou_subete(self, zscore_retsu: List[str], kromu_z_retsu: List[str]) -> Dict[str, pd.DataFrame]:
        out = {}
        for sheet in [self.male_sheet, self.female_sheet]:
            out[sheet] = self.shori_ichibu(sheet, zscore_retsu, kromu_z_retsu)
        return out


# ================= Analyzer =================
class Analyzer:
    def __init__(self, analysis_dir: Path, log_dir: Optional[PathLike] = None):
        self.analysis_dir = Path(analysis_dir)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir = Path(log_dir) if log_dir else self.analysis_dir / '_logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def soukan_bunseki(self, df: pd.DataFrame, seibetsu: str):
        print(f"[{seibetsu}] 分析中...")
        self.log(f"[{seibetsu}] 分析中...")  # 确保有日志输出
        # 添加其他分析逻辑

    def vif_bunseki(self, df: pd.DataFrame, columns: List[str], seibetsu: str):
        print(f"[{seibetsu}] 进行VIF分析...")
        self.log(f"[{seibetsu}] 进行VIF分析...")  # 确保有日志输出

    def ols_kouzou(self, df: pd.DataFrame, y_col: str, x_cols: List[str], seibetsu: str):
        print(f"[{seibetsu}] 进行OLS回归分析...")
        self.log(f"[{seibetsu}] 进行OLS回归分析...")  # 确保有日志输出
        # 添加其他分析逻辑

    def mixedlm_jikkou(self, df: pd.DataFrame, y_col: str, x_cols: List[str], group_col: str, seibetsu: str):
        print(f"[{seibetsu}] 进行混合效应模型分析...")
        self.log(f"[{seibetsu}] 进行混合效应模型分析...")  # 确保有日志输出
        # 添加其他分析逻辑


# ================= Plotter =================
class Plotter:
    def __init__(self, plot_dir: Path, tsuyo: bool = False):
        self.plot_dir = plot_dir
        self.plot_dir.mkdir(parents=True, exist_ok=True)
        self.tsuyo = tsuyo

    def histo_zu(self, df: pd.DataFrame, col: str, output_name: str, seibetsu: str):
        plt.figure(figsize=(8, 6))
        sns.histplot(df[col], kde=True)
        plt.title(f'{seibetsu} {col} 分布')
        plt.savefig(self.plot_dir / output_name)
        plt.close()
        print(f"[调试] 绘制直方图：{output_name}")
        self.log(f"[保存] 绘制直方图：{output_name}")  # 添加日志

    def santen_zu(self, df: pd.DataFrame, x_col: str, y_col: str, output_name: str, seibetsu: str):
        plt.figure(figsize=(8, 6))
        sns.scatterplot(x=df[x_col], y=df[y_col])
        plt.title(f'{seibetsu} {x_col} vs {y_col}')
        plt.savefig(self.plot_dir / output_name)
        plt.close()
        print(f"[调试] 绘制散点图：{output_name}")
        self.log(f"[保存] 绘制散点图：{output_name}")  # 添加日志


# ================= Main Execution =================
if __name__ == '__main__':
    from pathlib import Path
    from nipt_core import PathConfig, DataCleaner, Analyzer, Plotter, MaleBMIAnalyzer

    def shuyou():
        # 配置文件路径
        SRC_DIR = Path('./')
        RESULT = Path('./Result/AnalysisResult')
        CLEANED = Path('./Result/CleanResult')
        PLOTS = Path('./Result/Plots')
        LOGS = Path('./Result/CleanedLog')

        # 配置路径并确保路径存在
        cfg = PathConfig(SRC_DIR, RESULT, CLEANED, PLOTS, LOGS)
        cfg.ensure()
        print("[调试] 路径确保成功")

        # 数据清洗
        cleaner = DataCleaner(cfg, 文件名='附件.xlsx', 男胎表='男胎检测数据', 女胎表='女胎检测数据')
        print("[调试] 开始数据清洗...")
        df_dict = cleaner.jikkou_subete(
            zscore_retsu=['检测孕周', '孕妇BMI', '年龄', '生产次数'],
            kromu_z_retsu=['13号染色体的Z值', '18号染色体的Z值', '21号染色体的Z值', 'X染色体的Z值', 'Y染色体的Z值']
        )
        print('\n✅ 数据清洗完成')

        # 分析部分
        analyzer = Analyzer(cfg.kk_dr, cfg.log_dir)
        for sheet, df in df_dict.items():
            seibetsu = '男胎' if '男' in sheet else '女胎'
            print(f'\n===== 开始分析 {seibetsu} =====')
            if seibetsu == '男胎':
                analyzer.soukan_bunseki(df[['检测孕周', '孕妇BMI', '年龄', '生产次数', 'Y染色体浓度']], seibetsu)
                analyzer.vif_bunseki(df, ['检测孕周', '孕妇BMI', '年龄', '生产次数'], seibetsu)
                analyzer.ols_kouzou(df, 'Y染色体浓度', ['检测孕周', '孕妇BMI', '年龄', '生产次数'], seibetsu)
                analyzer.mixedlm_jikkou(df, 'Y染色体浓度', ['检测孕周', '孕妇BMI'], '孕妇代码', seibetsu)
            else:
                analyzer.soukan_bunseki(df[['X染色体的Z值', '13号染色体的Z值', '18号染色体的Z值', '21号染色体的Z值', '孕妇BMI', 'GC含量']], seibetsu)

        # 绘图部分
        plotter = Plotter(cfg.zu_dr, tsuyo=True)
        male_df = df_dict.get('男胎检测数据')
        if male_df is not None:
            print("[调试] 开始绘图...")
            plotter.histo_zu(male_df, '检测孕周', '男胎_孕周分布.png', '男胎')
            plotter.santen_zu(male_df, '检测孕周', 'Y染色体浓度', '男胎_孕周_vs_Y.png', '男胎')
            plotter.santen_zu(male_df, '孕妇BMI', 'Y染色体浓度', '男胎_BMI_vs_Y.png', '男胎')
        print('\n✅ 绘图完成')

        # 男胎 BMI 分析
        male_cleaned_xlsx = cfg.sr_dr / '男胎' / '男胎检测数据_cleaned.xlsx'
        if male_cleaned_xlsx.exists():
            print("[调试] 开始男胎 BMI 分析...")
            mba = MaleBMIAnalyzer(male_cleaned_xlsx, cfg.kk_dr)
            mba.jikkou_subete()
        else:
            print('【男胎】清洗输出缺失，跳过BMI/生存分析')

    shuyou()
