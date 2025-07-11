# bootstrap_stability.py
import pandas as pd
import numpy as np


def bootstrap_stability(df: pd.DataFrame, model, n_iterations: int = 1000):
    """
    进行 Bootstrap 稳定性分析
    :param df: 输入数据帧
    :param model: 拟合的模型
    :param n_iterations: 自助法采样次数
    """
    scores = []
    for i in range(n_iterations):
        # 随机采样
        sample = df.sample(n=len(df), replace=True)
        model.fit(sample)
        score = model.score(sample)  # 评分方法根据模型定义
        scores.append(score)

    # 输出 Bootstrap 稳定性
    print(f"Bootstrap 稳定性分析结果：均值={np.mean(scores)}, 方差={np.var(scores)}")

    return np.mean(scores), np.var(scores)
