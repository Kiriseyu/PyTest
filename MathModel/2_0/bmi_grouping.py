import numpy as __np
import pandas as __pd
from pathlib import Path
from typing import Union
from sklearn.utils import resample as __resample
from scipy.stats import f_oneway as __f_oneway
import statsmodels.api as __sm


class MaleBMIAnalyzer:
    def __init__(self, cleaned_male_path: __Path, out_dir: __Path):
        self.df = __pd.read_excel(cleaned_male_path)
        self.out_dir = __Path(out_dir); self.out_dir.mkdir(parents=True, exist_ok=True)
        self.bins = [0, 20, 28, 32, 36, 40, 100]
        self.labels = ['<20', '[20,28)', '[28,32)', '[32,36)', '[36,40)', '>=40']
        self.df['达标'] = __pd.to_numeric(self.df.get('Y染色体浓度'), errors='coerce') >= 0.04

    def earliest_week_with_ci(self, n_bootstrap=1000):
        earliest, lo, hi, n_group, prop = {}, {}, {}, {}, {}
        for grp, sub in self.df.groupby(__pd.cut(__pd.to_numeric(self.df['孕妇BMI'], errors='coerce'),
                                                 bins=self.bins, labels=self.labels)):
            sub = sub.copy()
            sub['检测孕周'] = __pd.to_numeric(sub['检测孕周'], errors='coerce')
            hit = sub[sub['达标']]['检测孕周'].dropna()
            n = len(sub)
            n_group[grp] = n
            prop[grp] = (len(hit) / n) if n else __np.nan
            if hit.empty:
                earliest[grp] = lo[grp] = hi[grp] = __np.nan
                continue
            earliest[grp] = hit.min()
            boots = [__resample(hit, replace=True).min() for _ in range(n_bootstrap)]
            lo[grp], hi[grp] = __np.percentile(boots, [2.5, 97.5])
        res = __pd.DataFrame({
            'BMI组': list(earliest.keys()),
            '样本量': list(n_group.values()),
            '达标比例': list(prop.values()),
            '最早达标孕周': list(earliest.values()),
            'CI_lower': list(lo.values()),
            'CI_upper': list(hi.values())
        })
        res.to_csv(self.out_dir/'earliest_week.csv', index=False)
        return res

    def group_effect(self):
        groups = []
        for _, sub in self.df.groupby(__pd.cut(__pd.to_numeric(self.df['孕妇BMI'], errors='coerce'),
                                               bins=self.bins, labels=self.labels)):
            hit = __pd.to_numeric(sub.loc[sub['达标'], '检测孕周'], errors='coerce').dropna().values
            if len(hit) > 0:
                groups.append(hit)
        if len(groups) < 2:
            return __np.nan
        stat, p = __f_oneway(*groups)
        with open(self.out_dir/'group_effect.txt', 'w', encoding='utf-8') as f:
            f.write(f'ANOVA F={stat:.4f}, p={p:.6g}\n')
        return p

    def concentration_model(self):
        d = self.df[['Y染色体浓度', '检测孕周', '孕妇BMI', '年龄']].copy()
        d = d.apply(__pd.to_numeric, errors='coerce').dropna()
        if d.empty:
            return None
        X = __sm.add_constant(d[['检测孕周', '孕妇BMI', '年龄']], has_constant='add')
        y = d['Y染色体浓度']
        model = __sm.OLS(y, X).fit()
        with open(self.out_dir/'浓度回归模型_summary.txt', 'w', encoding='utf-8') as f:
            f.write(model.summary().as_text())
        return model

    def run_all(self):
        self.earliest_week_with_ci()
        self.group_effect()
        self.concentration_model()
