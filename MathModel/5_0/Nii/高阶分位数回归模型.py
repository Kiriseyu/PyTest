# quantile_regression.py
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.quantile_regression import QuantReg


def quantile_regression(df: pd.DataFrame, quantile: float, output_file: str):
    """
    建立高阶分位数回归模型，并计算回归系数
    :param df: 输入的数据帧
    :param quantile: 分位数（0.975等）
    :param output_file: 输出文件路径
    """
    # 设置回归公式
    formula = 'Y染色体浓度 ~ 检测孕周 + 孕妇BMI + 检测孕周:孕妇BMI'

    # 进行分位数回归
    model = QuantReg.from_formula(formula, data=df)
    res = model.fit(q=quantile)

    # 输出回归系数
    print(f"Quantile {quantile} 回归系数：\n{res.params}")

    # 保存回归系数
    res_summary = res.summary().as_text()
    with open(output_file, 'w') as f:
        f.write(res_summary)
