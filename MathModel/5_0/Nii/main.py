# main.py
import os
from pathlib import Path
import pandas as pd

# 导入所有任务的脚本
from BMI分组绘图 import plot_bmi_grouping
from BMI分组绘图2 import plot_new_bmi_grouping
from 广义线性模型 import glmm_aic_bic_comparison
from 高阶分位数回归模型 import quantile_regression
from 男胎复合分组 import male_bmi_decision_tree
from 绘制分组检测时点 import group_recommendations

def main():
    # 确保结果文件夹存在
    result_dir = Path('./Result')
    result_dir.mkdir(parents=True, exist_ok=True)

    # 1. 绘制 BMI 分组图
    df = pd.read_excel('数据.xlsx')
    plot_bmi_grouping(df, result_dir / 'BMI分组图.png')

    # 2. 绘制新的 BMI 分组图
    plot_new_bmi_grouping(df, result_dir / '新的BMI分组图.png')

    # 3. AIC/BIC 模型比较
    glmm_aic_bic_comparison(df, result_dir / 'AIC_BIC_comparison.png')

    # 4. 高阶分位数回归
    quantile_regression(df, 0.975, result_dir / 'quantile_regression_summary.txt')

    # 5. 男胎 BMI 复合分组决策树
    male_bmi_decision_tree(df, result_dir / '男胎BMI决策树.png')

    # 6. 给出分组推荐检测时点
    group_recommendations(df, result_dir / '推荐检测时点.xlsx')

    print('所有任务已成功完成！')

if __name__ == '__main__':
    main()
