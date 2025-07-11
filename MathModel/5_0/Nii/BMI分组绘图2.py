# bmi_grouping_new.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_new_bmi_grouping(df: pd.DataFrame, output_file: str):
    """
    根据新的 BMI 分组标准进行绘图
    :param df: 输入的数据帧
    :param output_file: 输出文件路径
    """
    bins = [0, 30, 33, 36, 40]
    labels = ['超重', '肥胖1级', '肥胖2级', '肥胖3级']
    df['BMI_Group_New'] = pd.cut(df['孕妇BMI'], bins=bins, labels=labels)

    # 绘制新的 BMI 分组的柱状图
    plt.figure(figsize=(8, 6))
    sns.countplot(x='BMI_Group_New', data=df, palette="Set3")
    plt.title('新的 BMI 分组分布')
    plt.savefig(output_file)
