import os
import pandas as pd
import numpy as np
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

    # ========== 1. 描述性统计 ==========
    def descriptive_stats(self, df: pd.DataFrame, gender: str):
        desc = df.describe(include="all")
        save_path = os.path.join(self.analysis_dir, f"{gender}_描述统计.xlsx")
        desc.to_excel(save_path)
        print(f"[描述统计] {gender} -> {save_path}")

    # ========== 2. 正态性检验 ==========
    def normality_test(self, df: pd.DataFrame, cols: list, gender: str):
        results = {}
        for col in cols:
            if col not in df.columns:
                print(f"[正态性] {gender} 列 {col} 不存在，跳过")
                continue
            data = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(data) < 10:
                print(f"[正态性] {gender} 列 {col} 数据量不足，跳过")
                continue
            stat, p = stats.shapiro(data)
            results[col] = {"W-stat": stat, "p-value": p}

        if results:
            save_path = os.path.join(self.analysis_dir, f"{gender}_正态性检验.xlsx")
            pd.DataFrame(results).T.to_excel(save_path)
            print(f"[正态性] {gender} -> {save_path}")

    # ========== 3. 多重共线性 (VIF) ==========
    def vif_analysis(self, df: pd.DataFrame, x_cols: list, gender: str):
        X = df[x_cols].apply(pd.to_numeric, errors="coerce").dropna()
        X = X.loc[:, X.nunique() > 1]  # 去除常数列
        if X.empty:
            print(f"[VIF] {gender} 自变量不可用（全空或全常数），跳过")
            return
        X = sm.add_constant(X, has_constant='add')

        vif_data = pd.DataFrame()
        vif_data["feature"] = X.columns
        vif_data["VIF"] = [variance_inflation_factor(X.values, i)
                           for i in range(X.shape[1])]

        save_path = os.path.join(self.analysis_dir, f"{gender}_VIF.xlsx")
        vif_data.to_excel(save_path, index=False)
        print(f"[VIF] {gender} -> {save_path}")

    # ========== 4. Pearson 相关分析 ==========
    def correlation_analysis(self, df: pd.DataFrame, gender: str):
        corr = df.apply(pd.to_numeric, errors="coerce").corr(method="pearson")
        save_path = os.path.join(self.analysis_dir, f"{gender}_相关矩阵.xlsx")
        corr.to_excel(save_path)
        print(f"[相关矩阵] {gender} -> {save_path}")

    # ========== 5. 多元线性回归 ==========
    def linear_regression(self, df: pd.DataFrame, y_col: str, x_cols: list, gender: str):
        X = df[x_cols].apply(pd.to_numeric, errors="coerce")
        y = pd.to_numeric(df[y_col], errors="coerce")
        mask = y.notna()
        for c in X.columns:
            mask &= X[c].notna()
        X = X.loc[mask]
        y = y.loc[mask]

        if X.empty:
            print(f"[线性回归] {gender} 无有效样本，跳过")
            return

        X = sm.add_constant(X, has_constant='add')
        model = sm.OLS(y, X).fit()

        # 系数保存
        coef_path = os.path.join(self.analysis_dir, f"{gender}_线性回归_系数.xlsx")
        coef_df = pd.DataFrame(model.params, columns=["Estimate"])
        coef_df["StdErr"] = model.bse
        coef_df["t-value"] = model.tvalues
        coef_df["p-value"] = model.pvalues
        coef_df.to_excel(coef_path)

        # 摘要保存
        summary_path = os.path.join(self.analysis_dir, f"{gender}_线性回归_摘要.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(model.summary().as_text())

        print(f"[线性回归] {gender} 完成 -> {coef_path} | {summary_path}")

    # ========== 6. 线性混合模型 ==========
    def mixedlm(self, df: pd.DataFrame, y_col: str, x_cols: list, group_col: str, gender: str):
        # 仅取数值并对齐非空
        data = df[[y_col, group_col] + x_cols].copy()
        for c in x_cols + [y_col]:
            data[c] = pd.to_numeric(data[c], errors="coerce")
        data = data.dropna(subset=[y_col] + x_cols + [group_col])

        if data.empty or data[group_col].nunique() < 2:
            print(f"[混合模型] {gender} 数据不足或分组不足，跳过")
            return

        formula = f"{y_col} ~ {' + '.join(x_cols)}"
        try:
            model = smf.mixedlm(formula, data, groups=data[group_col])
            result = model.fit()

            # 系数保存
            coef_path = os.path.join(self.analysis_dir, f"{gender}_混合模型_系数.xlsx")
            result_df = pd.DataFrame(result.params, columns=["Estimate"])
            result_df["StdErr"] = result.bse
            result_df.to_excel(coef_path)

            # 摘要保存
            summary_path = os.path.join(self.analysis_dir, f"{gender}_混合模型_摘要.txt")
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(result.summary().as_text())

            print(f"[混合模型] {gender} 完成 -> {coef_path} | {summary_path}")

        except Exception as e:
            print(f"[混合模型] {gender} 失败: {e}")
