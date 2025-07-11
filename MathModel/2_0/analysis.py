import os
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats


class Analyzer:
    def __init__(self, analysis_dir: str, log_dir: str = None):
        self.analysis_dir = analysis_dir
        self.log_dir = log_dir or os.path.join(analysis_dir, "_logs")
        os.makedirs(self.analysis_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

    def correlation_matrix(self, df: pd.DataFrame, gender: str, cols: list):
        corr = df[cols].apply(pd.to_numeric, errors="coerce").corr(method="pearson")
        save_path = os.path.join(self.analysis_dir, f"{gender}_相关矩阵.xlsx")
        corr.to_excel(save_path)
        print(f"[相关矩阵] {gender} -> {save_path}")

    def vif(self, df: pd.DataFrame, x_cols: list, gender: str):
        X = df[x_cols].apply(pd.to_numeric, errors="coerce").dropna()
        X = X.loc[:, X.nunique() > 1]
        if X.empty:
            print(f"[VIF] {gender} 自变量不可用，跳过")
            return
        X = sm.add_constant(X, has_constant='add')
        vif_data = pd.DataFrame({
            'feature': X.columns,
            'VIF': [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
        })
        save_path = os.path.join(self.analysis_dir, f"{gender}_VIF.xlsx")
        vif_data.to_excel(save_path, index=False)
        print(f"[VIF] {gender} -> {save_path}")

    def ols(self, df: pd.DataFrame, y_col: str, x_cols: list, gender: str):
        X = df[x_cols].apply(pd.to_numeric, errors="coerce")
        y = pd.to_numeric(df[y_col], errors="coerce")
        mask = y.notna()
        for c in x_cols:
            mask &= X[c].notna()
        X, y = X.loc[mask], y.loc[mask]
        if X.empty:
            print(f"[OLS] {gender} 无有效样本，跳过")
            return
        X = sm.add_constant(X, has_constant='add')
        model = sm.OLS(y, X).fit()
        coef_path = os.path.join(self.analysis_dir, f"{gender}_OLS_系数.xlsx")
        pd.DataFrame({
            'Estimate': model.params,
            'StdErr': model.bse,
            't': model.tvalues,
            'p': model.pvalues
        }).to_excel(coef_path)
        summary_path = os.path.join(self.analysis_dir, f"{gender}_OLS_摘要.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(model.summary().as_text())
        print(f"[OLS] {gender} 完成 -> {coef_path} | {summary_path}")

    def mixedlm(self, df: pd.DataFrame, y_col: str, x_cols: list, group_col: str, gender: str):
        data = df[[y_col, group_col] + x_cols].copy()
        for c in x_cols + [y_col]:
            data[c] = pd.to_numeric(data[c], errors="coerce")
        data = data.dropna(subset=[y_col] + x_cols + [group_col])
        if data.empty or data[group_col].nunique() < 2:
            print(f"[MixedLM] {gender} 数据不足或分组不足，跳过")
            return
        formula = f"{y_col} ~ {' + '.join(x_cols)}"
        model = smf.mixedlm(formula, data, groups=data[group_col])
        result = model.fit()
        coef_path = os.path.join(self.analysis_dir, f"{gender}_MixedLM_系数.xlsx")
        pd.DataFrame({
            'Estimate': result.params,
            'StdErr': result.bse
        }).to_excel(coef_path)
        summary_path = os.path.join(self.analysis_dir, f"{gender}_MixedLM_摘要.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(result.summary().as_text())
        print(f"[MixedLM] {gender} 完成 -> {coef_path} | {summary_path}")
