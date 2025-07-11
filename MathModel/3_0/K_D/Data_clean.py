import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建可视化结果文件夹
os.makedirs("Distribution_Plots", exist_ok=True)


def perform_normality_tests(data, output_dir="Distribution_Plots"):
    """
    执行Shapiro-Wilk正态性检验并生成结果表

    参数:
    data: 清洗后的DataFrame
    output_dir: 输出目录

    返回:
    包含正态性检验结果的DataFrame
    """
    # 需要检查的变量列表
    variables_to_check = [
        '检测孕周', '孕妇BMI', '原始读段数', '在参考基因组上比对的比例',
        '重复读段的比例', '唯一比对的读段数', 'GC含量', '13号染色体的Z值',
        '18号染色体的Z值', '21号染色体的Z值', 'X染色体的Z值', 'Y染色体的Z值',
        'Y染色体浓度', 'X染色体浓度', '13号染色体的GC含量', '18号染色体的GC含量', '21号染色体的GC含量'
    ]

    # 确保变量在数据中存在
    available_vars = [var for var in variables_to_check if var in data.columns]

    # 执行正态性检验
    results = []
    for var in available_vars:
        var_data = data[var].dropna()
        stat, p_value = stats.shapiro(var_data)

        # 确定显著性水平
        if p_value < 0.001:
            significance = "***"
        elif p_value < 0.01:
            significance = "**"
        elif p_value < 0.05:
            significance = "*"
        else:
            significance = "N/A"

        # 判断是否正态分布
        is_normal = p_value > 0.05

        results.append({
            '变量名称': var,
            '统计量': round(stat, 4),
            'P值': round(p_value, 4),
            '显著性': significance,
            '是否正态分布': '是' if is_normal else '否'
        })

    # 创建结果DataFrame
    results_df = pd.DataFrame(results)

    # 保存结果到Excel
    results_file = f"{output_dir}/正态性检验结果表.xlsx"
    results_df.to_excel(results_file, index=False)
    print(f"正态性检验结果表已保存到 {results_file}")

    return results_df


def plot_distribution_checks(data, normality_results, output_dir="Distribution_Plots"):
    """
    绘制数据分布检验的可视图

    参数:
    data: 清洗后的DataFrame
    normality_results: 正态性检验结果DataFrame
    output_dir: 输出目录
    """
    # 将正态性检验结果转换为字典格式
    normality_dict = {}
    for _, row in normality_results.iterrows():
        normality_dict[row['变量名称']] = {
            'statistic': row['统计量'],
            'pvalue': row['P值'],
            'normal': row['是否正态分布'] == '是'
        }

    # 需要检查的变量列表
    variables_to_check = list(normality_dict.keys())

    # 确保变量在数据中存在
    available_vars = [var for var in variables_to_check if var in data.columns]

    # 计算每行显示的变量数量（4个）
    n_cols = 4
    n_rows = (len(available_vars) + n_cols - 1) // n_cols

    # 创建综合的可视化报告
    fig, axes = plt.subplots(n_rows, n_cols * 2, figsize=(20, 5 * n_rows))
    axes = axes.reshape(n_rows, n_cols * 2)

    for i, var in enumerate(available_vars):
        row = i // n_cols
        col = (i % n_cols) * 2

        # 获取数据
        var_data = data[var].dropna()

        # 直方图
        axes[row, col].hist(var_data, bins=30, density=True, alpha=0.7, color='skyblue')

        # 添加正态分布曲线
        xmin, xmax = axes[row, col].get_xlim()
        x = np.linspace(xmin, xmax, 100)
        p = stats.norm.pdf(x, var_data.mean(), var_data.std())
        axes[row, col].plot(x, p, 'k', linewidth=2)

        axes[row, col].set_title(f'{var} - 直方图')
        axes[row, col].set_ylabel('密度')

        # Q-Q图
        stats.probplot(var_data, dist="norm", plot=axes[row, col + 1])
        axes[row, col + 1].set_title(f'{var} - Q-Q图')

        # 添加正态性检验结果
        result = normality_dict.get(var, {})
        normal_text = "正态分布" if result.get('normal', False) else "非正态分布"
        p_text = f"p值={result.get('pvalue', 'N/A')}"

        # 在直方图上添加文本
        axes[row, col].text(0.05, 0.95, f"{normal_text}\n{p_text}",
                            transform=axes[row, col].transAxes,
                            bbox=dict(boxstyle="round,pad=0.3",
                                      facecolor="green" if result.get('normal', False) else "red", alpha=0.5))

    # 隐藏多余的子图
    for i in range(len(available_vars), n_rows * n_cols):
        row = i // n_cols
        col = (i % n_cols) * 2
        axes[row, col].set_visible(False)
        axes[row, col + 1].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/distribution_checks_all.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 为每个变量创建单独的详细图表
    for var in available_vars:
        var_data = data[var].dropna()

        # 创建单独的图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # 直方图
        n, bins, patches = ax1.hist(var_data, bins=30, density=True, alpha=0.7, color='skyblue')

        # 添加正态分布曲线
        xmin, xmax = ax1.get_xlim()
        x = np.linspace(xmin, xmax, 100)
        p = stats.norm.pdf(x, var_data.mean(), var_data.std())
        ax1.plot(x, p, 'k', linewidth=2)

        ax1.set_title(f'{var} - 直方图')
        ax1.set_ylabel('密度')
        ax1.set_xlabel('值')

        # Q-Q图
        stats.probplot(var_data, dist="norm", plot=ax2)
        ax2.set_title(f'{var} - Q-Q图')

        # 获取正态性检验结果
        result = normality_dict.get(var, {})
        stat_value = result.get('statistic', 'N/A')
        p_value = result.get('pvalue', 'N/A')
        normality = "是" if result.get('normal', False) else "否"

        # 添加检验结果
        fig.text(0.5, 0.01, f'Shapiro-Wilk检验: 统计量={stat_value}, p值={p_value}, 是否正态分布={normality}',
                 ha='center', fontsize=12,
                 bbox=dict(facecolor='green', alpha=0.5) if result.get('normal', False) else dict(facecolor='red',
                                                                                                  alpha=0.5))

        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        plt.savefig(f"{output_dir}/{var}_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()

        print(f"已保存 {var} 的分布检验图")


def prepare_and_clean_data(file_path, output_path):
    """
    数据准备与清洗函数

    参数:
    file_path: Excel文件路径
    output_path: 输出Excel文件路径

    返回:
    清洗后的DataFrame
    """
    # 读取数据
    df = pd.read_excel(file_path, sheet_name="男胎检测数据")

    # 1. 处理缺失值
    # 对于数值列，使用中位数填充
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    imputer_numeric = SimpleImputer(strategy='median')
    df[numeric_cols] = imputer_numeric.fit_transform(df[numeric_cols])

    # 对于分类列，使用众数填充
    categorical_cols = df.select_dtypes(include=['object']).columns
    imputer_categorical = SimpleImputer(strategy='most_frequent')
    df[categorical_cols] = imputer_categorical.fit_transform(df[categorical_cols])

    # 2. 处理日期列
    date_cols = ['末次月经', '检测日期']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
            df[f'{col}_year'] = df[col].dt.year
            df[f'{col}_month'] = df[col].dt.month
            df[f'{col}_day'] = df[col].dt.day

    # 3. 编码分类变量
    le = LabelEncoder()
    for col in categorical_cols:
        if col not in date_cols:  # 跳过日期列
            df[col] = le.fit_transform(df[col].astype(str))

    # 4. 确保响应变量在(0,1)范围内
    response_vars = ['Y染色体浓度', 'X染色体浓度']
    for var in response_vars:
        if var in df.columns:
            # 处理边界值
            df[var] = np.clip(df[var], 1e-5, 1 - 1e-5)

    # 5. 创建孕妇ID的数值编码（用于随机效应）
    if '孕妇代码' in df.columns:
        df['孕妇ID'] = le.fit_transform(df['孕妇代码'])

    # 6. 删除不必要的列
    cols_to_drop = ['序号', '末次月经', '检测日期', '孕妇代码']
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

    # 保存清洗后的数据为Excel格式，避免中文乱码
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='清洗后数据')

    return df


# 使用示例
if __name__ == "__main__":
    file_path = "附件.xlsx"
    output_path = "CL/cleaned_data.xlsx"

    # 数据清洗
    cleaned_data = prepare_and_clean_data(file_path, output_path)
    print("数据清洗完成，已保存为CL/cleaned_data.xlsx")

    # 执行正态性检验
    normality_results = perform_normality_tests(cleaned_data)
    print("正态性检验完成")

    # 绘制分布检验图
    plot_distribution_checks(cleaned_data, normality_results)
    print("数据分布检验图已保存到Distribution_Plots文件夹")

    # 打印正态性检验结果摘要
    print("\n正态性检验结果摘要:")
    print("=" * 80)
    normal_count = sum(normality_results['是否正态分布'] == '是')
    non_normal_count = len(normality_results) - normal_count
    print(f"正态分布变量数量: {normal_count}")
    print(f"非正态分布变量数量: {non_normal_count}")

    if normal_count > 0:
        print("\n正态分布的变量:")
        for _, row in normality_results[normality_results['是否正态分布'] == '是'].iterrows():
            print(f"  {row['变量名称']}: p值={row['P值']}")