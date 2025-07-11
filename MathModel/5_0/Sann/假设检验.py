# hypothesis_testing.py
import pandas as pd
from scipy import stats


def perform_hypothesis_testing(df: pd.DataFrame, columns: list):
    """
    对指定列进行 t 检验
    :param df: 输入数据帧
    :param columns: 需要进行 t 检验的列
    """
    results = {}
    for col in columns:
        group1 = df[col].dropna()  # 假设我们使用该列的非空值进行检验
        t_stat, p_value = stats.ttest_1samp(group1, 0)  # 单样本t检验
        results[col] = (t_stat, p_value)
        print(f"{col} - t-statistic: {t_stat}, p-value: {p_value}")

    return results
