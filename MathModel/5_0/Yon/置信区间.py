# bootstrap_ci.py
import numpy as np
import pandas as pd


def bootstrap_ci(df: pd.DataFrame, target: str, n_iterations: int = 1000, confidence_level: float = 0.95):
    """
    使用 Bootstrap 置信区间算法比较染色体 Z 值
    :param df: 输入数据帧
    :param target: 目标列
    :param n_iterations: 迭代次数
    :param confidence_level: 置信区间
    """
    values = df[target].dropna()
    sample_means = []

    for _ in range(n_iterations):
        sample = np.random.choice(values, size=len(values), replace=True)
        sample_means.append(np.mean(sample))

    lower_percentile = (1 - confidence_level) / 2
    upper_percentile = 1 - lower_percentile

    lower_bound = np.percentile(sample_means, lower_percentile * 100)
    upper_bound = np.percentile(sample_means, upper_percentile * 100)

    print(f"{target} 的 {confidence_level * 100}% 置信区间：({lower_bound}, {upper_bound})")

    return lower_bound, upper_bound
