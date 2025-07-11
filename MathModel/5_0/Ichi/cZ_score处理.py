# zscore_processing.py
import pandas as pd
from scipy import stats

def process_zscore(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    对指定列进行Z-score标准化处理
    :param df: 输入数据帧
    :param columns: 需要进行Z-score处理的列
    :return: 标准化后的数据帧
    """
    df_zscore = df.copy()
    for col in columns:
        if col in df.columns:
            df_zscore[f'{col}_z'] = stats.zscore(df[col].dropna())
        else:
            print(f"列 {col} 不存在，跳过")
    return df_zscore
