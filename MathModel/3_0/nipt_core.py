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
    def __init__(self, bunseki_dr: PathLike, rogu_dr: Optional[PathLike]=None):
        self.analysis_dir = Path(bunseki_dr)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir = Path(rogu_dr) if rogu_dr else self.analysis_dir / '_logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def toukei_gaiyou(self, df: pd.DataFrame, seibetsu: str):
        keiro = self.analysis_dir / f'{seibetsu}_描述统计.xlsx'
        df.describe(include='all').to_excel(keiro)
        print(f'[描述统计] {seibetsu} -> {keiro}')

    def seijoudo_kensa(self, df: pd.DataFrame, retsu: List[str], seibetsu: str):
        from statsmodels.stats.diagnostic import lilliefors
        gyou = []
        for col in retsu:
            if col not in df.columns:
                continue
            x = pd.to_numeric(df[col], errors='coerce').dropna()
            if len(x) < 8:
                continue
            if len(x) <= 5000:
                W, pval = stats.shapiro(x); hou = 'Shapiro'
            else:
                W, pval = lilliefors(x); hou = 'Lilliefors'
            gyou.append({'col': col, 'stat': W, 'p': pval, 'method': hou})
        if gyou:
            out = pd.DataFrame(gyou)
            keiro = self.analysis_dir / f'{seibetsu}_正态性检验.xlsx'
            out.to_excel(keiro, index=False)
            print(f'[正态性] {seibetsu} -> {keiro}')

    def vif_bunseki(self, df: pd.DataFrame, x_retsu: List[str], seibetsu: str):
        tokuchou = df[x_retsu].apply(pd.to_numeric, errors='coerce').dropna()
        tokuchou = tokuchou.loc[:, tokuchou.nunique() > 1]
        if tokuchou.empty:
            print(f'[VIF] {seibetsu} 无有效自变量')
            return
        tokuchou = sm.add_constant(tokuchou, has_constant='add')
        vif = pd.DataFrame({
            'feature': tokuchou.columns,
            'VIF': [variance_inflation_factor(tokuchou.values, i) for i in range(tokuchou.shape[1])]
        })
        vif = vif[vif['feature'] != 'const']
        keiro = self.analysis_dir / f'{seibetsu}_VIF.xlsx'
        vif.to_excel(keiro, index=False)
        print(f'[VIF] {seibetsu} -> {keiro}')

    def soukan_bunseki(self, df: pd.DataFrame, seibetsu: str):
        keiro = self.analysis_dir / f'{seibetsu}_相关矩阵.xlsx'
        df.apply(pd.to_numeric, errors='coerce').corr(method='pearson').to_excel(keiro)
        print(f'[相关矩阵] {seibetsu} -> {keiro}')

    def ols_kouzou(self, df: pd.DataFrame, y_retsu: str, x_retsu: List[str], seibetsu: str):
        tokuchou = df[x_retsu].apply(pd.to_numeric, errors='coerce')
        ryou = pd.to_numeric(df[y_retsu], errors='coerce')
        masuku = ryou.notna()
        for c in tokuchou.columns:
            masuku &= tokuchou[c].notna()
        tokuchou, ryou = (tokuchou.loc[masuku], ryou.loc[masuku])
        if tokuchou.empty:
            print(f'[OLS] {seibetsu} 无样本')
            return
        tokuchou = sm.add_constant(tokuchou, has_constant='add')
        moderu = sm.OLS(ryou, tokuchou).fit()
        coef = pd.DataFrame(moderu.params, columns=['Estimate'])
        coef['StdErr'], coef['t-value'], coef['p-value'] = (moderu.bse, moderu.tvalues, moderu.pvalues)
        coef.to_excel(self.analysis_dir / f'{seibetsu}_OLS_系数.xlsx')
        with open(self.analysis_dir / f'{seibetsu}_OLS_摘要.txt', 'w', encoding='utf-8') as f:
            f.write(moderu.summary().as_text())
        print(f'[OLS] {seibetsu} -> 样本数={len(tokuchou)}  已导出系数与摘要')

    def mixedlm_jikkou(self, df: pd.DataFrame, y_retsu: str, x_retsu: List[str], group_retsu: str, seibetsu: str):
        data = df[[y_retsu, group_retsu] + x_retsu].copy()
        for c in x_retsu + [y_retsu]:
            data[c] = pd.to_numeric(data[c], errors='coerce')
        data = data.dropna(subset=[y_retsu] + x_retsu + [group_retsu])
        if data.empty or data[group_retsu].nunique() < 2:
            print(f'[MixedLM] {seibetsu} 数据不足')
            return
        kou = f"{y_retsu} ~ {' + '.join(x_retsu)}"
        try:
            kekka = smf.mixedlm(kou, data, groups=data[group_retsu]).fit()
            dfc = pd.DataFrame(kekka.params, columns=['Estimate'])
            dfc['StdErr'] = kekka.bse
            dfc.to_excel(self.analysis_dir / f'{seibetsu}_MixedLM_系数.xlsx')
            with open(self.analysis_dir / f'{seibetsu}_MixedLM_摘要.txt', 'w', encoding='utf-8') as f:
                f.write(kekka.summary().as_text())
            print(f'[MixedLM] {seibetsu} -> 样本数={len(data)}  已导出系数与摘要')
        except Exception as e:
            print(f'[MixedLM] {seibetsu} 失败: {e}')

# ================= Plotter =================
class Plotter:
    def __init__(self, kiso_dr: PathLike, tsuyo: bool=True):
        self.base_dir = Path(kiso_dr)
        self.enable = tsuyo
        setup_chinese()

    def _save(self, fig, keiro_png: Path):
        if not self.enable:
            plt.close(fig); return
        keiro_png.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(keiro_png, dpi=300, bbox_inches='tight')
        try:
            fig.savefig(keiro_png.with_suffix('.svg'), bbox_inches='tight')
        except Exception:
            pass
        plt.close(fig)

    def histo_zu(self, df: pd.DataFrame, retsu: str, shutsu: str, seibetsu: str):
        if retsu not in df.columns:
            return
        s = pd.to_numeric(df[retsu], errors='coerce').dropna()
        if s.empty:
            return
        fig = plt.figure(figsize=(6, 4))
        sns.histplot(s, kde=True)
        plt.title(f'{retsu} 直方图')
        self._save(fig, self.base_dir / seibetsu / shutsu)

    def santen_zu(self, df: pd.DataFrame, x_retsu: str, y_retsu: str, shutsu: str, seibetsu: str):
        if x_retsu not in df.columns or y_retsu not in df.columns:
            return
        xs = pd.to_numeric(df[x_retsu], errors='coerce')
        ys = pd.to_numeric(df[y_retsu], errors='coerce')
        masuku = xs.notna() & ys.notna()
        if not masuku.any():
            return
        fig = plt.figure(figsize=(6, 4))
        plt.scatter(xs[masuku], ys[masuku], s=14)
        plt.xlabel(x_retsu); plt.ylabel(y_retsu)
        plt.title(f'{x_retsu} vs {y_retsu}')
        self._save(fig, self.base_dir / seibetsu / shutsu)

# ================= Male BMI Analyzer =================
class MaleBMIAnalyzer:
    def __init__(self, otoko_xlsx: PathLike, sy_dr: PathLike):
        self.df = pd.read_excel(Path(otoko_xlsx))
        self.out_dir = Path(sy_dr)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.df['达标'] = pd.to_numeric(self.df['Y染色体浓度'], errors='coerce') >= 0.04
        self.bins = [0, 20, 28, 32, 36, 40, 100]
        self.labels = ['<20', '[20,28)', '[28,32)', '[32,36)', '[36,40)', '>=40']
        print('【男胎Y浓度描述】\n', self.df['Y染色体浓度'].describe())

    def saishou_shu_CI(self, n_boot: int=1000) -> pd.DataFrame:
        hajime, ci_l, ci_u, nmap, pmap = ({}, {}, {}, {}, {})
        for grp, sub in self.df.groupby(pd.cut(self.df['孕妇BMI'], bins=self.bins, labels=self.labels)):
            ok = sub[sub['达标']]
            gw = pd.to_numeric(ok['检测孕周'], errors='coerce').dropna()
            nmap[grp] = len(sub)
            pmap[grp] = float(ok.shape[0]) / max(1, len(sub))
            if gw.empty:
                hajime[grp] = ci_l[grp] = ci_u[grp] = np.nan
            else:
                hajime[grp] = float(gw.min())
                samps = [float(resample(gw).min()) for _ in range(n_boot)]
                ci_l[grp], ci_u[grp] = (np.percentile(samps, 2.5), np.percentile(samps, 97.5))
        res = pd.DataFrame({
            'BMI组': list(hajime.keys()),
            '样本量': list(nmap.values()),
            '达标比例': list(pmap.values()),
            '最早达标孕周': list(hajime.values()),
            'CI_lower': list(ci_l.values()),
            'CI_upper': list(ci_u.values())
        })
        res.to_csv(self.out_dir / 'earliest_week.csv', index=False)
        print('[男胎BMI] 最早达标孕周+95%CI 导出 -> earliest_week.csv')
        return res

    def ichiji_tassei_tbl(self) -> pd.DataFrame:
        hitsuyou = ['孕妇代码', '检测孕周', 'Y染色体浓度', '孕妇BMI']
        for c in hitsuyou:
            if c not in self.df.columns:
                self.df[c] = np.nan
        gyou = []
        for pid, g in self.df.groupby('孕妇代码', sort=False):
            g = g.sort_values('检测孕周')
            ok = g[pd.to_numeric(g['Y染色体浓度'], errors='coerce') >= 0.04]
            if not ok.empty:
                w = float(pd.to_numeric(ok['检测孕周'], errors='coerce').iloc[0])
                bmi0 = float(pd.to_numeric(g['孕妇BMI'], errors='coerce').iloc[0])
                gyou.append({'孕妇代码': pid, '达标孕周': w, 'BMI': bmi0})
        dfh = pd.DataFrame(gyou)
        if dfh.empty:
            return dfh
        dfh['BMI_group'] = pd.cut(dfh['BMI'], bins=self.bins, labels=self.labels)
        return dfh

    def bmi_hakozu(self, dfh: pd.DataFrame):
        if dfh.empty:
            print('[BMI箱线图] 无“首次达标孕周”样本，略过')
            return
        setup_chinese()
        plt.figure(figsize=(7, 4))
        sns.boxplot(x='BMI_group', y='达标孕周', data=dfh, showfliers=False)
        sns.pointplot(x='BMI_group', y='达标孕周', data=dfh, estimator=np.mean, errorbar='ci', markers='D')
        plt.title('不同BMI组首次达标孕周分布（含均值及95%CI）')
        plt.xlabel('BMI组'); plt.ylabel('首次达标孕周')
        outp = self.out_dir / 'BMI_group_box.png'
        outp.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(outp, dpi=300, bbox_inches='tight')
        plt.close()
        print(f'[BMI箱线图] 已导出 -> {outp}')

    def gurupu_kouka(self):
        gun = []
        for _, sub in self.df.groupby(pd.cut(self.df['孕妇BMI'], bins=self.bins, labels=self.labels)):
            gw = pd.to_numeric(sub.loc[sub['达标'], '检测孕周'], errors='coerce').dropna().values
            if gw.size > 0:
                gun.append(gw)
        if len(gun) < 2:
            print('[分组效果] 样本不足'); return None
        F, pval = stats.f_oneway(*gun)
        with open(self.out_dir / 'group_effect.txt', 'w', encoding='utf-8') as f:
            f.write(f'F={F}, p={pval}\n')
        print(f'[分组效果] ANOVA F={F:.2f}, p={pval:.3g}  -> group_effect.txt')
        return pval

    def noudo_moderu(self):
        df = self.df.dropna(subset=['Y染色体浓度', '检测孕周', '孕妇BMI', '年龄'])
        tokuchou = df[['检测孕周', '孕妇BMI', '年龄']]
        ryou = df['Y染色体浓度']
        X_sm = sm.add_constant(tokuchou)
        moderu = sm.OLS(ryou, X_sm).fit()
        (self.out_dir / '浓度回归模型_summary.txt').write_text(moderu.summary().as_text(), encoding='utf-8')
        pd.Series(moderu.params, name='beta').to_csv(self.out_dir / '浓度回归系数.csv')
        print('[浓度模型] R²(训练内) ≈ {:.3f}  -> 摘要/系数已导出'.format(LinearRegression().fit(tokuchou, ryou).score(tokuchou, ryou)))
        return moderu

    def seizon_saiteki(self):
        csv_p = self.out_dir.parent / 'CleanResult' / '男胎' / 'cleaned_survival_data.csv'
        if not csv_p.exists():
            print('[生存分析] 未找到 cleaned_survival_data.csv'); return None
        best = seizon_saiteki_keisan(csv_p, self.out_dir / 'survival')
        dfh = self.ichiji_tassei_tbl()
        self.bmi_hakozu(dfh)
        return best

    def jikkou_subete(self):
        self.saishou_shu_CI()
        self.gurupu_kouka()
        self.noudo_moderu()
        self.seizon_saiteki()
        print('[男胎BMI] 全部检验完成！')

# ================= Survival helpers =================
def saiteki_shu(jikan: np.ndarray, jiken: np.ndarray, mokuhyo: float=0.95) -> float:
    order = np.argsort(jikan)
    jikan, jiken = (np.array(jikan)[order], np.array(jiken)[order])
    if jiken.sum() == 0:
        return float(jikan[-1])
    kum = np.cumsum(jiken) / jiken.sum()
    idx = np.where(kum >= mokuhyo)[0]
    return float(jikan[idx[0]] if len(idx) else jikan[-1])

def km_zu_group(df: pd.DataFrame, sy_dr: Path):
    if df.empty or 'group' not in df.columns:
        print('[KM曲线] 数据为空或缺少分组，跳过'); return
    setup_chinese()
    kmf = KaplanMeierFitter()
    plt.figure(figsize=(7, 4))
    for g, sub in df.groupby('group'):
        t = pd.to_numeric(sub['time'], errors='coerce')
        e = pd.to_numeric(sub['event'], errors='coerce')
        t, e = (t.dropna(), e.loc[t.index])
        if len(t) == 0:
            continue
        kmf.fit(t, event_observed=e, label=f'组别 {g}')
        kmf.plot(ci_show=True)
    plt.title('Kaplan–Meier 曲线：未达标概率（按PI分组）')
    plt.xlabel('孕周'); plt.ylabel('未达标概率')
    outp = Path(sy_dr) / 'KM_curve.png'
    outp.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(outp, dpi=300, bbox_inches='tight'); plt.close()
    print(f'[KM曲线] 已导出 -> {outp}')

def seizon_saiteki_keisan(csv_p: PathLike, sy_dr: PathLike, n_boot: int=1000, mokuhyo: float=0.95, rand: int=42):
    sy_dr = Path(sy_dr); sy_dr.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(csv_p)
    nokori = ['time', 'event', 'bmi', 'age', 'weight', 'parity']
    df_fit = df[nokori].dropna()
    cph = CoxPHFitter(); cph.fit(df_fit, duration_col='time', event_col='event')
    cph.summary.to_csv(sy_dr / 'cox_summary.csv')
    coef = cph.params_
    for k in ['bmi', 'age', 'weight', 'parity']:
        df[k] = df[k].fillna(0)
    df['PI'] = coef['bmi'] * df['bmi'] + coef['age'] * df['age'] + coef['weight'] * df['weight'] + coef['parity'] * df['parity']
    tc = df[['PI']].values; rb = df['event'].values
    dt = DecisionTreeClassifier(max_depth=2, min_samples_leaf=0.1, random_state=rand)
    dt.fit(tc, rb)
    raw_thr = list(dt.tree_.threshold[dt.tree_.threshold != -2])
    thr = sorted({float(t) for t in raw_thr if np.isfinite(t)})
    (Path(sy_dr) / 'tree_thresholds.txt').write_text(f'raw={raw_thr}\nused={thr}\n', encoding='utf-8')

    def three_labels_cut(seri, cuts):
        edges = [-np.inf] + cuts + [np.inf]
        return pd.cut(seri, bins=edges, labels=['低', '中', '高'])

    if len(thr) >= 2:
        cuts = thr[:2]
        if cuts[0] < cuts[1]:
            df['group'] = three_labels_cut(df['PI'], cuts)
        else:
            try:
                df['group'] = pd.qcut(df['PI'], q=3, labels=['低', '中', '高'], duplicates='drop')
            except Exception:
                df['group'] = pd.cut(df['PI'], bins=3, labels=['低', '中', '高'])
    elif len(thr) == 1:
        mid = float(np.median(df['PI']))
        cuts = sorted([thr[0], mid])
        if cuts[0] == cuts[1]:
            try:
                df['group'] = pd.qcut(df['PI'], q=3, labels=['低', '中', '高'], duplicates='drop')
            except Exception:
                df['group'] = pd.cut(df['PI'], bins=3, labels=['低', '中', '高'])
        else:
            df['group'] = three_labels_cut(df['PI'], cuts)
    else:
        try:
            df['group'] = pd.qcut(df['PI'], q=3, labels=['低', '中', '高'], duplicates='drop')
        except Exception:
            df['group'] = pd.cut(df['PI'], bins=3, labels=['低', '中', '高'])

    best, ci = ({}, {})
    rng = np.random.RandomState(rand)
    for g, sub in df.groupby('group'):
        best[g] = saiteki_shu(sub['time'].values, sub['event'].values, mokuhyo=mokuhyo)
        stats_g = []
        for _ in range(n_boot):
            boot = resample(sub, replace=True, random_state=rng)
            stats_g.append(saiteki_shu(boot['time'].values, boot['event'].values, mokuhyo=mokuhyo))
        ci[g] = (float(np.percentile(stats_g, 2.5)), float(np.percentile(stats_g, 97.5)))
    df['recommended_time'] = df['group'].map(best)
    df.to_excel(sy_dr / 'final_grouping_and_timing.xlsx', index=False)
    matome = pd.DataFrame({
        '推荐孕周': pd.Series(best),
        'CI下限': pd.Series({k: v[0] for k, v in ci.items()}),
        'CI上限': pd.Series({k: v[1] for k, v in ci.items()})
    })
    matome.to_excel(sy_dr / 'bootstrap_best_time.xlsx')
    print('[生存分析] 分组与最佳时点:', best)
    km_zu_group(df[['time', 'event', 'group']].copy(), sy_dr)
    return best

# ================= Female CV =================
def onna_bunrui_cv(onna_xlsx: PathLike, sy_dr: PathLike, bunretsu: int=5, rand: int=42):
    sy_dr = Path(sy_dr); sy_dr.mkdir(parents=True, exist_ok=True)
    df = pd.read_excel(onna_xlsx)
    tokuchou = ['X染色体的Z值', '13号染色体的Z值', '18号染色体的Z值', '21号染色体的Z值', '孕妇BMI', 'GC含量', '唯一比对的读段数']
    raw = df['染色体的非整倍体'].astype(str).str.strip().str.upper()

    def map_label(s: str):
        if s == '' or s == 'NAN':
            return 0
        if s.startswith('T'):
            return 1
        return None

    rb = raw.map(map_label)
    tc = df[tokuchou].apply(pd.to_numeric, errors='coerce')
    tc = tc.fillna(tc.median(numeric_only=True))
    masuku = rb.notna()
    tc, rb = (tc.loc[masuku], rb.loc[masuku].astype(int))
    print('[女胎] 标签分布(Txx=1, 空白=0)：', rb.value_counts().to_dict())
    if rb.nunique() < 2:
        print('[女胎] 仍只有单类，无法二分类。'); return

    cls = rb.value_counts()
    max_s = int(cls.min())
    bunretsu = min(bunretsu, max(2, max_s))
    skf = StratifiedKFold(n_splits=bunretsu, shuffle=True, random_state=rand)

    def pick_threshold(y_shin, y_kakuritsu):
        p, r, thr = precision_recall_curve(y_shin, y_kakuritsu)
        f1 = 2 * p * r / (p + r + 1e-12)
        idx = int(np.nanargmax(f1))
        return 0.5 if idx >= len(thr) else float(thr[idx])

    def eval_with_threshold(y_shin, y_kakuritsu, genkai):
        y_yoso = (y_kakuritsu >= genkai).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_shin, y_yoso, labels=[0, 1]).ravel()
        acc = (tp + tn) / max(1, tp + tn + fp + fn)
        rec = tp / max(1, tp + fn)
        pre = tp / max(1, tp + fp)
        auc = roc_auc_score(y_shin, y_kakuritsu)
        spe = tn / max(1, tn + fp)
        return ({'acc': acc, 'recall': rec, 'precision': pre, 'specificity': spe, 'auc': auc, 'thr': genkai}, y_yoso)

    def _plot_cm(y_shin, y_yoso, keiro: Path, tag: str):
        setup_chinese()
        cm = confusion_matrix(y_shin, y_yoso, labels=[0, 1])
        plt.figure(figsize=(4.2, 3.6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['预测0', '预测1'], yticklabels=['实际0', '实际1'])
        plt.title(f'{tag} 混淆矩阵')
        plt.tight_layout(); plt.savefig(keiro, dpi=300, bbox_inches='tight'); plt.close()
        print(f'[女胎-{tag}] 混淆矩阵 -> {keiro}')

    def cv_model(tag: str, build_model):
        gyou, gens = ([], [])
        for tr, te in skf.split(tc, rb):
            Xtr, Xte = (tc.iloc[tr], tc.iloc[te])
            ytr, yte = (rb.iloc[tr], rb.iloc[te])
            if ytr.nunique() < 2 or yte.nunique() < 2:
                print(f'[女胎-{tag}] 某折仅单一类别，跳过'); continue
            md = build_model().fit(Xtr, ytr)
            proba = md.predict_proba(Xte)[:, 1]
            thr = pick_threshold(yte, proba); gens.append(thr)
            met, _ = eval_with_threshold(yte, proba, thr); gyou.append(met)
        if not gyou:
            print(f'[女胎-{tag}] 无有效折'); return
        dfm = pd.DataFrame(gyou)
        keiro = sy_dr / f'女胎_{tag}_cv.csv'
        dfm.to_csv(keiro, index=False)
        print(
            f'[女胎-{tag}] CV均值: acc={dfm.acc.mean():.3f}±{dfm.acc.std():.3f}  '
            f'precision={dfm.precision.mean():.3f}±{dfm.precision.std():.3f}  '
            f'recall={dfm.recall.mean():.3f}±{dfm.recall.std():.3f}  '
            f'specificity={dfm["specificity"].mean():.3f}±{dfm["specificity"].std():.3f}  '
            f'auc={dfm.auc.mean():.3f}±{dfm.auc.std():.3f}  thr≈{np.median(gens):.3f} -> {keiro}'
        )
        pd.Series(gens, name='best_threshold').to_csv(sy_dr / f'女胎_{tag}_cv_thresholds.csv', index=False)

        best_thr = float(np.median(gens))
        Xtr, Xte, ytr, yte = train_test_split(tc, rb, test_size=0.3, random_state=42, stratify=rb)
        mdl = build_model().fit(Xtr, ytr)
        proba_te = mdl.predict_proba(Xte)[:, 1]

        setup_chinese(); RocCurveDisplay.from_predictions(yte, proba_te)
        plt.title(f'女胎-{tag}-ROC'); plt.savefig(sy_dr / f'女胎_{tag}_ROC.png'); plt.close()

        PrecisionRecallDisplay.from_predictions(yte, proba_te)
        plt.title(f'女胎-{tag}-PR'); plt.savefig(sy_dr / f'女胎_{tag}_PR.png'); plt.close()

        met, ypred_te = eval_with_threshold(yte, proba_te, best_thr)
        _plot_cm(yte, ypred_te, sy_dr / f'女胎_{tag}_CM.png', tag=f'{tag}(thr={best_thr:.3f})')
        (sy_dr / f'女胎_{tag}_recommended_threshold.txt').write_text(f'{best_thr:.6f}', encoding='utf-8')

    cv_model('LR', lambda: LogisticRegression(max_iter=5000, class_weight='balanced'))
    cv_model('RF', lambda: RandomForestClassifier(n_estimators=600, random_state=rand, class_weight='balanced'))
    print('✅ 女胎交叉验证（不平衡增强版 + 混淆矩阵）已导出')
