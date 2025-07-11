# bmi_grouping.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_bmi_grouping(df: pd.DataFrame, output_file: str):
    """
    根据 BMI 分组并进行绘图
    :param df: 输入的数据帧
    :param output_file: 输出文件路径
    """
    bins = [0, 18.5, 25.0, 30.0, 40.0]
    labels = ['低体重', '正常体重', '超重', '肥胖']
    df['BMI_Group'] = pd.cut(df['孕妇BMI'], bins=bins, labels=labels)

    # 绘制 BMI 分组的柱状图
    plt.figure(figsize=(8, 6))
    sns.countplot(x='BMI_Group', data=df, palette="Set2")
    plt.title('BMI 分组分布')
    plt.savefig(output_file)
