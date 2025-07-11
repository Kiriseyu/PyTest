# pi_coefficient_analysis.py
import pandas as pd


def pi_coefficient_analysis(df: pd.DataFrame, pi_column: str):
    """
    对 PI 系数进行描述性统计分析
    :param df: 输入数据帧
    :param pi_column: PI 系数列名
    """
    pi_stats = df[pi_column].describe()
    print(f"PI系数描述性统计：\n{pi_stats}")

    # 输出统计结果
    pi_stats.to_csv('pi_coefficient_stats.csv')
    return pi_stats
