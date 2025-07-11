# group_threshold_curve.py
import pandas as pd
import matplotlib.pyplot as plt

def group_threshold_curve(df: pd.DataFrame, pi_column: str, threshold: float, output_file: str):
    """
    绘制 PI 值分组达标曲线
    :param df: 输入数据帧
    :param pi_column: PI 系数列名
    :param threshold: 达标阈值
    :param output_file: 输出图像文件路径
    """
    df['Threshold_Group'] = df[pi_column] >= threshold

    # 绘制达标曲线
    plt.figure(figsize=(10, 6))
    df.groupby('Threshold_Group')[pi_column].plot(kind='density', label='达标与否')
    plt.title(f'PI值达标曲线（阈值: {threshold}）')
    plt.legend()
    plt.savefig(output_file)
