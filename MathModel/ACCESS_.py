import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib import rcParams
from pathlib import Path

# -------------- 字体 --------------
def setup_font():
    rcParams['axes.unicode_minus'] = False
    try:
        rcParams['font.family'] = 'SimHei'
    except:
        rcParams['font.sans-serif'] = ['DejaVu Sans']
        rcParams['font.serif'] = ['DejaVu Serif']

setup_font()

# -------------- 核心类 --------------
class NIPTPlotter:
    def __init__(self, xlsx_path: str, out_dir: str):
        self.xlsx_path = Path(xlsx_path)
        self.out_dir   = Path(out_dir)
        self.df_male: pd.DataFrame = None
        self.df_female: pd.DataFrame = None
        self._load()
        self._prep_dirs()

    # ---------- 私有工具 ----------
    def _load(self):
        self.df_male   = pd.read_excel(self.xlsx_path, sheet_name='男胎检测数据')
        self.df_female = pd.read_excel(self.xlsx_path, sheet_name='女胎检测数据')
        for df in (self.df_male, self.df_female):
            df['weeks_float'] = (
                df['检测孕周'].astype(str)
                .str.replace('＋', '+')
                .map(self._weekstr2float)
            )

    @staticmethod
    def _weekstr2float(s: str):
        try:
            w, d = s.split('+')
            return int(w) + int(d) / 7
        except:
            return np.nan

    def _prep_dirs(self):
        (self.out_dir / 'male').mkdir(parents=True, exist_ok=True)
        (self.out_dir / 'female').mkdir(parents=True, exist_ok=True)

    def _savefig(self, fig: plt.Figure, subdir: str, name: str):
        folder = self.out_dir / subdir
        # 只保存为 png 格式
        fig.savefig(folder / f'{name}.png', dpi=300, bbox_inches='tight')
        plt.close(fig)

    # ---------- 所有单功能绘图 ----------
    def plot_missing_heatmap(self, df, title, subdir):
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(df.isnull(), cbar=False, cmap=['white', 'black'], ax=ax)
        ax.set_title(f'{title} - 缺失值热图')
        self._savefig(fig, subdir, '01_missing_heatmap')

    def plot_y_conc_dist(self, df, subdir):
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(df['Y染色体浓度'], kde=True, bins=30, ax=ax)
        ax.axvline(0.04, color='red', ls='--', label='4% 阈值')
        ax.legend()
        ax.set_title('男婴 Y 染色体浓度分布')
        self._savefig(fig, subdir, '02_y_conc_dist')

    def plot_week_vs_y(self, df, subdir):
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.scatterplot(x=df['检测孕周'], y=df['Y染色体浓度'], ax=ax)
        ax.axhline(0.04, color='red', ls='--')
        ax.set_xlabel('孕周'), ax.set_ylabel('Y 浓度')
        ax.set_title('孕周 vs Y 浓度')
        self._savefig(fig, subdir, '03_week_vs_y')

    def plot_bmi_vs_y(self, df, subdir):
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.scatterplot(x=df['孕妇BMI'], y=df['Y染色体浓度'], ax=ax)
        ax.axhline(0.04, color='red', ls='--')
        ax.set_title('BMI vs Y 浓度')
        self._savefig(fig, subdir, '04_bmi_vs_y')

    def plot_corr_heatmap(self, df, cols, subdir):
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(df[cols].corr(), annot=True, fmt='.2f', cmap='coolwarm', ax=ax)
        ax.set_title('相关系数矩阵')
        self._savefig(fig, subdir, '05_corr_heatmap')

    def plot_z_dist(self, df, chrom, subdir):
        col = f'{chrom}号染色体的Z值'
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(df[col], kde=True, bins=30, ax=ax)
        ax.axvline(3, color='red', ls='--', label='Z=3')
        ax.axvline(-3, color='red', ls='--')
        ax.legend()
        ax.set_title(f'{chrom} 号染色体 Z 值分布')
        self._savefig(fig, subdir, f'06_z{chrom}_dist')

    def plot_z_vs_abn(self, df, chrom, subdir):
        col = f'{chrom}号染色体的Z值'
        abn = df['染色体的非整倍体'].notnull()
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.boxplot(x=abn, y=df[col], ax=ax)
        ax.set_xticklabels(['正常', '异常'])
        ax.set_title(f'{chrom} 号 Z 值 vs 非整倍体')
        self._savefig(fig, subdir, f'07_z{chrom}_vs_abn')

    # ---------- GC ----------
    def count_gc_ge(self, df) -> int:
        return (df['GC含量'] >= 0.4).sum()

    def plot_gc_hist(self, df, title, subdir):
        gc_round = df['GC含量'].dropna().round(3)
        s = gc_round.value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(14, 4))
        bars = ax.bar(s.index, s.values, width=0.0008,
                      color='steelblue', edgecolor='white')
        for b in bars:
            h = b.get_height()
            if h:
                ax.text(b.get_x()+0.0004, h, int(h), ha='center', va='bottom', fontsize=7)
        ax.axvline(0.4, color='red', ls='--')
        ax.set_title(f'{title} - GC 含量分布')
        ax.tick_params(axis='x', rotation=90, labelsize=6)
        self._savefig(fig, subdir, '08_gc_hist')

    # ---------- 孕周风险饼图 ----------
    def plot_week_risk_pie(self, df, title, subdir):
        """
        1. 把「检测孕周」拆成 周、天 两列
        2. 用 weeks_int + days_int/7 得到浮点孕周
        3. 按浮点孕周分层画饼图
        """

        # ---- 1. 拆分「周」「天」----
        def parse_week_day(s):
            if pd.isna(s):
                return np.nan, np.nan
            try:
                # 去掉中文 w/W，统一大小写
                s = str(s).replace('W', 'w').replace('＋', '+')
                week_part, day_part = s.split('w+')
                return int(week_part), int(day_part)
            except:
                return np.nan, np.nan

        df[['weeks_int', 'days_int']] = (
            df['检测孕周'].apply(parse_week_day)
            .apply(pd.Series)
        )

        # ---- 2. 浮点孕周（已存在列可复用）----
        df['weeks_float'] = df['weeks_int'] + df['days_int'] / 7

        # ---- 3. 分层 ----
        valid = df['weeks_float'].dropna()
        if valid.empty:
            print(f'[{title}] 无有效孕周，跳过饼图')
            return

        bins = [0, 12, 27, np.inf]
        labels = ['风险较低', '风险高', '风险极高']
        counts = (
            pd.cut(valid, bins=bins, labels=labels)
            .value_counts()
            .reindex(labels, fill_value=0)
        )

        # ---- 4. 绘图 ----
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(counts, labels=counts.index, autopct='%1.1f%%',
               colors=['#2ca02c', '#ff7f0e', '#d62728'])
        ax.set_title(f'{title} - 孕周风险分布')
        self._savefig(fig, subdir, '09_week_risk_pie')

    # ---------- IVF 妊娠分类柱形图 ----------
    def plot_ivf_bar(self, df, title, subdir):
        """
        对 IVF妊娠 列做 value_counts() 后画柱形图
        预期取值：自然受孕 / IUI（人工授精） / IVF（试管婴儿）
        """
        if 'IVF妊娠' not in df.columns:
            print(f'[{title}] 无 IVF妊娠 列，跳过')
            return

        counts = df['IVF妊娠'].dropna().value_counts()

        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(
            counts.index.astype(str),
            counts.values,
            color=['#2ca02c', '#ff7f0e', '#1f77b4'][:len(counts)],
            edgecolor='black'
        )

        # 柱顶标数量
        for b in bars:
            h = b.get_height()
            ax.text(b.get_x() + b.get_width()/2, h + max(counts)*0.01,
                    int(h), ha='center', va='bottom')

        ax.set_xlabel('受孕方式')
        ax.set_ylabel('样本数量')
        ax.set_title(f'{title} - IVF妊娠分布')
        self._savefig(fig, subdir, '10_ivf_bar')

# -------------- 单功能启动 --------------
def main():
    plotter = NIPTPlotter(
        xlsx_path=r'C:\Users\26790\Desktop\Result\AnalysisResult\附件_孕周格式修改.xlsx',
        out_dir=r'C:\Users\26790\Desktop\Result\Plotting'
    )

    # 把想跑的函数设成 True 即可
    tasks = {
        'missing_heatmap': False,
        'y_conc_dist':     False,
        'week_vs_y':       True,
        'bmi_vs_y':        True,
        'corr_heatmap':    False,
        'z_dist_13':       True,
        'z_dist_18':       True,
        'z_dist_21':       True,
        'z_vs_abn_13':     False,
        'z_vs_abn_18':     False,
        'z_vs_abn_21':     False,
        'gc_hist':         False,
        'week_risk_pie':   False,
        'ivf_bar': True,
    }

    m, f = plotter.df_male, plotter.df_female
    corr_cols = ['weeks_float', '孕妇BMI', 'Y染色体浓度', 'GC含量']

    if tasks['missing_heatmap']:
        plotter.plot_missing_heatmap(m, '男婴', 'male')
        plotter.plot_missing_heatmap(f, '女婴', 'female')
    if tasks['y_conc_dist']:
        plotter.plot_y_conc_dist(m, 'male')
    if tasks['week_vs_y']:
        plotter.plot_week_vs_y(m, 'male')
    if tasks['bmi_vs_y']:
        plotter.plot_bmi_vs_y(m, 'male')
    if tasks['corr_heatmap']:
        plotter.plot_corr_heatmap(m, corr_cols, 'male')
        plotter.plot_corr_heatmap(f, corr_cols, 'female')
    for ch in (13, 18, 21):
        if tasks[f'z_dist_{ch}']:
            plotter.plot_z_dist(m if ch == 21 else f, ch, 'male' if ch == 21 else 'female')
        if tasks[f'z_vs_abn_{ch}']:
            plotter.plot_z_vs_abn(f, ch, 'female')
    if tasks['gc_hist']:
        print('男胎 GC≥0.4 数量：', plotter.count_gc_ge(m))
        print('女胎 GC≥0.4 数量：', plotter.count_gc_ge(f))
        plotter.plot_gc_hist(m, '男婴', 'male')
        plotter.plot_gc_hist(f, '女婴', 'female')
    if tasks['week_risk_pie']:
        plotter.plot_week_risk_pie(m, '男婴', 'male')
        plotter.plot_week_risk_pie(f, '女婴', 'female')
    if tasks['ivf_bar']:
        plotter.plot_ivf_bar(m, '男婴', 'male')
        plotter.plot_ivf_bar(f, '女婴', 'female')

    print('>>> 所选图形已保存')

if __name__ == '__main__':
    main()