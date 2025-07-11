# pi_group_distribution.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def pi_group_distribution(df: pd.DataFrame, pi_column: str, output_file: str):
    """
    绘制按 PI 值分组后的分布图
    :param df: 输入数据帧
    :param pi_column: PI 系数列名
    :param output_file: 输出图像文件路径
    """
    # 分组
    bins = [df[pi_column].min(), 0.25, 0.5, 0.75, df[pi_column].max()]
    labels = ['低', '中', '高', '超高']
    df['PI_Group'] = pd.cut(df[pi_column], bins=bins, labels=labels)

    # 绘制分布图
    plt.figure(figsize=(10, 6))
    sns.histplot(df['PI_Group'], kde=False, bins=4, color='blue')
    plt.title('PI值分组分布')
    plt.savefig(output_file)
