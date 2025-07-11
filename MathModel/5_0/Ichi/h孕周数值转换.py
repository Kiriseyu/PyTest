# plot_gestational_age_vs_y.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_gestational_age_vs_y(df: pd.DataFrame, output_file: str):
    """
    绘制 孕周 vs Y 浓度散点图
    :param df: 输入的数据帧
    :param output_file: 输出文件路径
    """
    sns.scatterplot(x=df['检测孕周'], y=df['Y染色体浓度'])
    plt.title('孕周 vs Y浓度')
    plt.savefig(output_file)
