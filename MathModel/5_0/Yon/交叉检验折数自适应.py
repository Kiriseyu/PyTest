# 交叉检验折数自适应.py
import pandas as pd
from sklearn.model_selection import StratifiedKFold

def stratified_k_fold(df: pd.DataFrame, target: str, n_splits: int = 5):
    """
    使用分层交叉验证进行模型验证
    :param df: 输入数据帧
    :param target: 目标列（分类标签）
    :param n_splits: 折数
    """
    # 打印列名，确保目标列存在
    print(f"数据帧的列名: {df.columns.tolist()}")

    # 检查目标列是否存在
    if target not in df.columns:
        raise ValueError(f"目标列 '{target}' 未在数据中找到")

    # 特征和目标变量分离
    X = df.drop(target, axis=1)
    y = df[target]

    # 设置分层交叉验证
    skf = StratifiedKFold(n_splits=n_splits)

    # 执行分层交叉验证
    for train_index, test_index in skf.split(X, y):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        print(f"训练集大小: {len(X_train)}, 测试集大小: {len(X_test)}")

    return skf
