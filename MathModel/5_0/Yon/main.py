# main.py
import os
from pathlib import Path
import pandas as pd

# 导入所有任务的脚本
from 交叉检验折数自适应 import stratified_k_fold  # 正常导入自定义模块
from 逻辑回归性能指标 import logistic_regression
from 随机森林性能指标 import random_forest
from 绘制ROC曲线 import plot_roc_curve
from 绘制PR import plot_pr_curve
from 置信区间 import bootstrap_ci
from 绘制分布图 import plot_all_distributions

def main():
    # 确保结果文件夹存在
    result_dir = Path('./Result')
    result_dir.mkdir(parents=True, exist_ok=True)

    # 1. 设置文件路径（上级文件夹）
    excel_file = Path('../附件.xlsx')  # 使用相对路径指向上级文件夹

    # 检查文件是否存在
    if not excel_file.exists():
        print(f"错误: 文件 '{excel_file}' 未找到!")
        return

    # 2. 加载数据
    df = pd.read_excel(excel_file)  # 加载数据

    # 打印数据列名，帮助调试
    print(f"数据帧的列名: {df.columns.tolist()}")

    # 3. 执行其他任务
    stratified_k_fold(df, target='胎儿是否健康', n_splits=5)  # 修改为正确的目标列名
    logistic_regression(df, features=['孕妇BMI', '检测孕周'], target='胎儿是否健康')
    random_forest(df, features=['孕妇BMI', '检测孕周'], target='胎儿是否健康')
    plot_roc_curve(df, features=['孕妇BMI', '检测孕周'], target='胎儿是否健康', output_file=result_dir / 'roc_curve.png')
    plot_pr_curve(df, features=['孕妇BMI', '检测孕周'], target='胎儿是否健康', output_file=result_dir / 'pr_curve.png')
    bootstrap_ci(df, target='Y染色体的Z值')
    plot_all_distributions(df, result_dir)

    print('所有任务已成功完成！')

if __name__ == '__main__':
    main()
