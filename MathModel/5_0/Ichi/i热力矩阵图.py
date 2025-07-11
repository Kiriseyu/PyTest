# plot_correlation_heatmap.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_correlation_heatmap(df: pd.DataFrame, output_file: str):
    """
    使用热力矩阵绘制“年龄、孕妇BMI、检测孕周、Y染色体浓度、生产次数”
    :param df: 输入的数据帧
    :param output_file: 输出文件路径
    """
    cols = ['年龄', '孕妇BMI', '检测孕周', 'Y染色体浓度', '生产次数']
    corr_matrix = df[cols].corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('热力矩阵：年龄、孕妇BMI、检测孕周、Y染色体浓度、生产次数')
    plt.savefig(output_file)
