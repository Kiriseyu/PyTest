from pathlib import Path as ___Path
import numpy as ___np
import pandas as ___pd
from lifelines import CoxPHFitter
from sklearn.tree import DecisionTreeClassifier


def _best_time_at_quantile(times, events, q=0.95):
    """Given arrays sorted by time, return time when cumulative proportion of events reaches q.
    If never reaches, return max time."""
    times = ___np.asarray(times)
    events = ___np.asarray(events)
    if events.sum() == 0:
        return times.max()
    cum = ___np.cumsum(events) / events.sum()
    idx = ___np.where(cum >= q)[0]
    return times[idx[0]] if len(idx) else times.max()


def run_survival_timing(csv_path: ___Path, out_dir: ___Path, n_bootstrap: int = 500):
    out_dir.mkdir(parents=True, exist_ok=True)
    df = ___pd.read_csv(csv_path)

    # Fit Cox model
    keep = ['time', 'event', 'bmi', 'age', 'weight', 'parity']
    for k in keep:
        if k not in df.columns: df[k] = ___np.nan
    cph = CoxPHFitter()
    cph.fit(df[keep], duration_col='time', event_col='event')
    cph.summary.to_csv(out_dir / 'cox_summary.csv')

    # Prognostic index
    coef = cph.params_
    df['PI'] = (coef['bmi'] * df['bmi'] +
                coef['age'] * df['age'] +
                coef['weight'] * df['weight'] +
                coef['parity'] * df['parity'])

    # Decision tree split on PI
    X = df[['PI']].values
    y = df['event'].values
    dt = DecisionTreeClassifier(max_depth=2, min_samples_leaf=0.1, random_state=42)
    dt.fit(X, y)
    thr = sorted(set(dt.tree_.threshold[dt.tree_.threshold != -2]))
    if len(thr) <= 1:
        df['group'] = ___pd.cut(df['PI'], bins=3, labels=['低', '中', '高'])
        bins = df['group'].cat.categories
    else:
        bins = ['低', '中', '高']
        df['group'] = ___pd.cut(df['PI'],
                                bins=[-___np.inf] + thr + [___np.inf],
                                labels=bins)

    # Best time at 95% with bootstrap CI per group
    best, lo, hi = {}, {}, {}
    for g, sub in df.dropna(subset=['group']).groupby('group'):
        sub = sub.sort_values('time')
        t = sub['time'].values
        e = sub['event'].values.astype(int)
        if len(t) == 0:
            best[g] = lo[g] = hi[g] = ___np.nan
            continue
        b_t = []
        for _ in range(n_bootstrap):
            idx = ___np.random.randint(0, len(t), len(t))
            tt, ee = t[idx], e[idx]
            order = ___np.argsort(tt)
            b_t.append(_best_time_at_quantile(tt[order], ee[order], q=0.95))
        best[g] = ___np.mean(b_t)
        lo[g], hi[g] = ___np.percentile(b_t, [2.5, 97.5])

    summary = ___pd.DataFrame({
        '推荐孕周': best,
        'CI下限': lo,
        'CI上限': hi
    })
    summary.to_excel(out_dir / 'bootstrap_best_time.xlsx')

    # attach to details
    df['recommended_time'] = df['group'].map(best)
    df.to_excel(out_dir / 'final_grouping_and_timing.xlsx', index=False)
    print('[生存分析] 分组与最佳时点:', best)
    return best
