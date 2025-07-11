# plot_missing_value_heatmap.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_missing_value_heatmap(df: pd.DataFrame, output_file: str):
    """
    使用代码生成缺失值热力图观测缺失值
    :param df: 输入的数据帧
    :param output_file: 输出图片的路径
    """
    # 绘制缺失值热力图
    plt.figure(figsize=(12, 8))
    sns.heatmap(df.isnull(), cbar=False, cmap='viridis', yticklabels=False)
    plt.title('缺失值热力图', fontproperties='SimHei')
    plt.savefig(output_file)
