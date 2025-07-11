# perform_shapiro_wilk_test.py
import pandas as pd
from scipy import stats

def perform_shapiro_wilk_test(df: pd.DataFrame, columns: list):
    """
    进行Shapiro-Wilk检验
    :param df: 输入数据帧
    :param columns: 需要进行Shapiro-Wilk检验的列
    """
    for col in columns:
        stat, p_value = stats.shapiro(df[col].dropna())
        print(f'{col} - Shapiro-Wilk Test: stat={stat}, p-value={p_value}')
