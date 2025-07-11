# plot_z_value_distribution.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_z_value_distribution(df: pd.DataFrame, output_dir: str):
    """
    生成13/18/21号染色体的Z值分布图
    :param df: 输入的数据帧
    :param output_dir: 输出图片的路径
    """
    for col in ['13号染色体的Z值', '18号染色体的Z值', '21号染色体的Z值']:
        plt.figure(figsize=(8, 6))
        sns.histplot(df[col].abs(), kde=True)
        plt.title(f'{col} Z=|3| 分布')
        plt.savefig(f'{output_dir}/{col}_Z_abs_3.png')
