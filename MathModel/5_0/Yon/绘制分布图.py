# plot_distributions.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def plot_all_distributions(df: pd.DataFrame, output_dir: str):
    """
    绘制染色体 Z 值分布图、孕妇 BMI 分布图、GC 含量分布图
    :param df: 输入的数据帧
    :param output_dir: 输出文件夹路径
    """
    # 确保输出文件夹存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 1. 绘制染色体 Z 值分布图
    plt.figure(figsize=(8, 6))
    sns.histplot(df['Y染色体的Z值'], kde=True, color='blue')
    plt.title('Y染色体的Z值分布')
    plt.xlabel('Z值')
    plt.ylabel('频率')
    plt.savefig(f'{output_dir}/chromosome_z_distribution.png')
    plt.close()

    # 2. 绘制孕妇 BMI 分布图
    plt.figure(figsize=(8, 6))
    sns.histplot(df['孕妇BMI'], kde=True, color='green')
    plt.title('孕妇BMI分布')
    plt.xlabel('BMI值')
    plt.ylabel('频率')
    plt.savefig(f'{output_dir}/bmi_distribution.png')
    plt.close()

    # 3. 绘制 GC 含量分布图
    plt.figure(figsize=(8, 6))
    sns.histplot(df['GC含量'], kde=True, color='red')
    plt.title('GC含量分布')
    plt.xlabel('GC含量')
    plt.ylabel('频率')
    plt.savefig(f'{output_dir}/gc_content_distribution.png')
    plt.close()

    print("分布图已保存到:", output_dir)
