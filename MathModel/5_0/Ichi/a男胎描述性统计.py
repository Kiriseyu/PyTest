# analyze_male_baby_bmi.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_male_baby_bmi(data_file: str, output_file: str):
    """
    引入男胎描述性统计图进行分析
    :param data_file: 输入的男胎数据文件路径
    :param output_file: 输出图片的路径
    """
    # 读取数据
    df = pd.read_excel(data_file)

    # 描述性统计
    desc_stats = df.describe()
    print(desc_stats)

    # 绘制统计图
    sns.histplot(df['孕妇BMI'], kde=True)
    plt.title('男胎孕妇BMI分布')
    plt.savefig(output_file)
