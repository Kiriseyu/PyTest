# plot_bmi_vs_y.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_bmi_vs_y(df: pd.DataFrame, output_file: str):
    """
    绘制 BMI vs Y 浓度散点图
    :param df: 输入的数据帧
    :param output_file: 输出文件路径
    """
    sns.scatterplot(x=df['孕妇BMI'], y=df['Y染色体浓度'])
    plt.title('BMI vs Y浓度')
    plt.savefig(output_file)
