# ols_model.py
import pandas as pd
import statsmodels.api as sm


def ols_model(df: pd.DataFrame, target: str, features: list):
    """
    使用 OLS 进行多元线性回归分析
    :param df: 数据帧
    :param target: 因变量
    :param features: 自变量列表
    :return: OLS 回归模型结果
    """
    X = df[features]
    X = sm.add_constant(X)  # 加入常数项
    y = df[target]

    model = sm.OLS(y, X).fit()
    print(f"\n多元线性回归结果：\n{model.summary()}")
    return model
