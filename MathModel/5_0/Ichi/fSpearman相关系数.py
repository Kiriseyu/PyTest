# perform_spearman_test.py
import pandas as pd
from scipy.stats import spearmanr

def perform_spearman_test(df: pd.DataFrame, col1: str, col2: str):
    """
    使用 Spearman 相关系数检验
    :param df: 输入数据帧
    :param col1: 第一个变量
    :param col2: 第二个变量
    """
    corr, p_value = spearmanr(df[col1], df[col2])
    print(f'Spearman Correlation between {col1} and {col2}: {corr}, p-value={p_value}')
