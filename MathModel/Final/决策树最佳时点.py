from pathlib import Path
import pandas as pd, numpy as np
from lifelines import CoxPHFitter
from sklearn.tree import DecisionTreeClassifier

def run_survival_timing(csv_path: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    survival_df = pd.read_csv(csv_path)

    # Cox
    cph = CoxPHFitter()
    cph.fit(survival_df[['time', 'event', 'bmi', 'age', 'weight', 'parity']],
            duration_col='time', event_col='event')
    cph.summary.to_csv(out_dir / 'cox_summary.csv')

    # PI
    coef = cph.params_
    survival_df['PI'] = (coef['bmi'] * survival_df['bmi'] +
                         coef['age'] * survival_df['age'] +
                         coef['weight'] * survival_df['weight'] +
                         coef['parity'] * survival_df['parity'])

    # 决策树分组
    X = survival_df[['PI']].values
    y = survival_df['event'].values
    dt = DecisionTreeClassifier(max_depth=2, min_samples_leaf=0.1, random_state=42)
    dt.fit(X, y)
    thr = sorted(set(dt.tree_.threshold[dt.tree_.threshold != -2]))
    if len(thr) <= 1:
        survival_df['group'] = pd.cut(survival_df['PI'], bins=3, labels=['低', '中', '高'])
    else:
        survival_df['group'] = pd.cut(survival_df['PI'],
                                      bins=[-np.inf] + thr + [np.inf],
                                      labels=['低', '中', '高'])

    # 最佳时点：累计达标≥95 %最早孕周
    best = {}
    for g, sub in survival_df.groupby('group'):
        times = np.sort(sub['time'])
        events = sub['event'].values[np.argsort(sub['time'])]
        cum_prop = np.cumsum(events) / events.sum()
        idx = np.where(cum_prop >= 0.95)[0]
        best[g] = times[idx[0]] if len(idx) else times[-1]
    survival_df['recommended_time'] = survival_df['group'].map(best)


    survival_df.to_excel(out_dir / 'final_grouping_and_timing.xlsx',
                         index=False, sheet_name='样本详情')
    summary_df = pd.DataFrame(best_times).T
    summary_df.columns = ['推荐孕周', 'CI下限', 'CI上限']
    summary_df.to_excel(out_dir / 'bootstrap_best_time.xlsx',
                        index=True, sheet_name='分组汇总')

    print('[生存分析] 分组与最佳时点:', best)
    return best
