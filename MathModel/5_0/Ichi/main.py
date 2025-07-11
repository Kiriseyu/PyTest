# main.py
import os
from pathlib import Path
import pandas as pd

# 导入所有任务的脚本
from a男胎描述性统计 import analyze_male_baby_bmi
from b缺失热力图 import plot_missing_value_heatmap
from cZ_score处理 import process_zscore
from d染色体Z值分布 import plot_z_value_distribution
from eWilk检验 import perform_shapiro_wilk_test
from fSpearman相关系数 import perform_spearman_test
from g浓度散点图 import plot_bmi_vs_y
from h孕周数值转换 import plot_gestational_age_vs_y
from i热力矩阵图 import plot_correlation_heatmap
from jVIF分析 import vif_analysis
from k多元线性模型求解 import ols_model
from l线性混合效应模型 import vif_analysis

def main():
    # 确保结果文件夹存在
    result_dir = Path('./Result')
    result_dir.mkdir(parents=True, exist_ok=True)

    # 1. 引入男胎描述性统计图进行分析
    analyze_male_baby_bmi('../男胎数据.xlsx', result_dir / '男胎_BMI_分布.png')

    # 2. 生成缺失值热力图
    df_male = pd.read_excel('../男胎数据.xlsx')
    plot_missing_value_heatmap(df_male, result_dir / '男胎缺失值热力图.png')

    # 3. Z-score 处理
    df = pd.read_excel('附录数据.xlsx')
    df_zscore = process_zscore(df, ['检测孕周', '孕妇BMI', '年龄', '生产次数'])
    df_zscore.to_excel(result_dir / '附录数据_zscore.xlsx', index=False)

    # 4. 绘制染色体 Z 值分布图
    plot_z_value_distribution(df, result_dir)

    # 5. Shapiro-Wilk 检验
    perform_shapiro_wilk_test(df, ['检测孕周', '孕妇BMI', '年龄'])

    # 6. Spearman 相关系数检验
    perform_spearman_test(df, '检测孕周', '孕妇BMI')

    # 7. 绘制 BMI vs Y 浓度散点图
    plot_bmi_vs_y(df, result_dir / 'BMI_vs_Y.png')

    # 8. 绘制孕周 vs Y 浓度散点图
    plot_gestational_age_vs_y(df, result_dir / '孕周_vs_Y.png')

    # 9. 孕周数值转换
    df['孕周数值'] = df['检测孕周'].apply(to_gw_float)

    # 10. 绘制热力矩阵图
    plot_correlation_heatmap(df, result_dir / '热力矩阵.png')

    # 11. VIF分析
    vif_columns = ['检测孕周', '孕妇BMI', '年龄', '生产次数']
    vif_analysis(df, vif_columns)

    # 12. 多元线性模型求解
    ols_model(df, 'Y染色体浓度', ['检测孕周', '孕妇BMI', '年龄', '生产次数'])

    # 13. 线性混合效应模型求解
    mixedlm_model(df, 'Y染色体浓度', ['检测孕周', '孕妇BMI'], '孕妇代码')

    print('所有任务已成功完成！')

if __name__ == '__main__':
    main()
