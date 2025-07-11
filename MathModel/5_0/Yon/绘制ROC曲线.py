# plot_roc_curve.py
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, auc


def plot_roc_curve(df: pd.DataFrame, features: list, target: str, output_file: str):
    """
    绘制 ROC 曲线
    :param df: 输入数据帧
    :param features: 特征列列表
    :param target: 目标列
    :param output_file: 输出文件路径
    """
    X = df[features]
    y = df[target]

    # 计算模型预测概率
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
    y_prob = model.predict_proba(X)[:, 1]

    fpr, tpr, _ = roc_curve(y, y_prob)
    roc_auc = auc(fpr, tpr)

    # 绘制 ROC 曲线
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='b', label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend(loc='lower right')
    plt.savefig(output_file)
    plt.close()
