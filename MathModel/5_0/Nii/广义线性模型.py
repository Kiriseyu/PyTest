# glmm_aic_bic.py
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf

def glmm_aic_bic_comparison(df: pd.DataFrame, output_file: str):
    """
    建立广义线性模型（基准/加法/交互），并计算 AIC/BIC
    :param df: 输入的数据帧
    :param output_file: 输出文件路径
    """
    # 基准模型
    baseline_model = smf.glm('Y染色体浓度 ~ 孕妇BMI + 检测孕周', data=df, family=sm.families.Gaussian()).fit()
    # 加法模型
    add_model = smf.glm('Y染色体浓度 ~ 孕妇BMI + 检测孕周 + 年龄', data=df, family=sm.families.Gaussian()).fit()
    # 交互模型
    interaction_model = smf.glm('Y染色体浓度 ~ 孕妇BMI * 检测孕周 + 年龄', data=df, family=sm.families.Gaussian()).fit()

    # 输出 AIC 和 BIC
    results = {
        "Model": ["Baseline", "Additive", "Interaction"],
        "AIC": [baseline_model.aic, add_model.aic, interaction_model.aic],
        "BIC": [baseline_model.bic, add_model.bic, interaction_model.bic]
    }
    results_df = pd.DataFrame(results)

    # 绘制 AIC/BIC 比较柱状图
    results_df.set_index('Model', inplace=True)
    results_df.plot(kind='bar', figsize=(10, 6))
    plt.title('AIC/BIC Model Comparison')
    plt.savefig(output_file)

    return results_df
