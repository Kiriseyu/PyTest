# vif_model.py
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor


def vif_analysis(df: pd.DataFrame, columns: list):
    """
    对多元回归模型的自变量进行 VIF 分析
    :param df: 数据帧
    :param columns: 自变量列
    :return: None
    """
    X = df[columns]
    X = sm.add_constant(X)  # 加入常数项
    vif_data = pd.DataFrame()
    vif_data["Variable"] = X.columns
    vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]

    print(f"VIF 分析结果：\n{vif_data}")
    vif_data.to_csv('vif_results.csv', index=False)
    return vif_data
