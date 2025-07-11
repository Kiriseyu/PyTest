# main.py
import os
from pathlib import Path
import pandas as pd

# 导入所有任务的脚本
from 假设检验 import perform_hypothesis_testing
from Cox特征分析 import cox_model_analysis
from PI描述性统计 import pi_coefficient_analysis
from PI分布图 import pi_group_distribution
from 达标曲线绘制 import group_threshold_curve
from Bootstrap分析 import bootstrap_stability


def main():
    # 确保结果文件夹存在
    result_dir = Path('./Result')
    result_dir.mkdir(parents=True, exist_ok=True)

    # 1. 假设检验
    df = pd.read_excel('数据.xlsx')
    hypothesis_results = perform_hypothesis_testing(df, ['年龄', '孕妇BMI', '生产次数'])

    # 2. Cox模型特征重要性分析
    cox_model_analyzer = cox_model_analysis(df, '检测孕周', '事件')

    # 3. PI系数描述性统计分析
    pi_stats = pi_coefficient_analysis(df, 'PI系数')

    # 4. PI值分组分布图
    pi_group_distribution(df, 'PI系数', result_dir / 'PI分组分布.png')

    # 5. 绘制达标曲线
    group_threshold_curve(df, 'PI系数', threshold=0.5, output_file=result_dir / 'PI达标曲线.png')

    # 6. Bootstrap 稳定性分析
    model = None  # 假设你已经有一个拟合好的模型
    bootstrap_stability(df, model)

    print('所有任务已成功完成！')


if __name__ == '__main__':
    main()
