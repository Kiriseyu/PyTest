# plot_pr_curve.py
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_recall_curve, average_precision_score


def plot_pr_curve(df: pd.DataFrame, features: list, target: str, output_file: str):
    """
    绘制 PR 曲线（精确率/召回率）
    :param df: 输入数据帧
    :param features: 特征列列表
    :param target: 目标列
    :param output_file: 输出文件路径
    """
    X = df[features]
    y = df[target]

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
    y_prob = model.predict_proba(X)[:, 1]

    precision, recall, _ = precision_recall_curve(y, y_prob)
    avg_precision = average_precision_score(y, y_prob)

    # 绘制 PR 曲线
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, color='b', label=f'PR curve (avg precision = {avg_precision:.2f})')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend(loc='lower left')
    plt.savefig(output_file)
    plt.close()
