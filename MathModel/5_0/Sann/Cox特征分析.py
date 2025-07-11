# cox_model_analysis.py
import pandas as pd
import matplotlib.pyplot as plt
from lifelines import CoxPHFitter


def cox_model_analysis(df: pd.DataFrame, duration_col: str, event_col: str):
    """
    使用 Cox 比例风险模型进行特征重要性分析
    :param df: 输入数据帧
    :param duration_col: 时间列
    :param event_col: 事件列
    """
    cph = CoxPHFitter()
    cph.fit(df, duration_col=duration_col, event_col=event_col)
    print(f"Cox 模型特征重要性：\n{cph.summary}")

    # 绘制特征系数图
    cph.plot()
    plt.title('Cox模型特征系数')
    plt.savefig('cox_model_coefficients.png')

    return cph
