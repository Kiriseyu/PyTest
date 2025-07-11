# random_forest.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix


def random_forest(df: pd.DataFrame, features: list, target: str):
    """
    使用随机森林模型进行训练，并输出分类报告
    :param df: 输入数据帧
    :param features: 特征列列表
    :param target: 目标列
    """
    X = df[features]
    y = df[target]

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
    y_pred = model.predict(X)

    # 输出分类报告
    report = classification_report(y, y_pred)
    print(f"随机森林模型分类报告：\n{report}")

    # 输出混淆矩阵
    cm = confusion_matrix(y, y_pred)
    print(f"混淆矩阵：\n{cm}")

    return model
