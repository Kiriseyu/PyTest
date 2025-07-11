# male_bmi_decision_tree.py
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree

def male_bmi_decision_tree(df: pd.DataFrame, output_file: str):
    """
    对男胎 BMI 进行决策树分析，输出决策图
    :param df: 输入的数据帧
    :param output_file: 输出文件路径
    """
    # 特征选择
    X = df[['孕妇BMI', '生产次数']]
    y = df['男胎类型']  # 假设目标变量是男胎类型

    # 决策树模型
    clf = DecisionTreeClassifier(max_depth=3)
    clf = clf.fit(X, y)

    # 绘制决策树图
    plt.figure(figsize=(12, 8))
    tree.plot_tree(clf, filled=True, feature_names=['孕妇BMI', '生产次数'], class_names=['男胎', '女胎'])
    plt.title('男胎BMI与生产次数决策树')
    plt.savefig(output_file)
