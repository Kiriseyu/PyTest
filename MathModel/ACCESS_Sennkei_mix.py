import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.gofplots import qqplot
from statsmodels.formula.api import mixedlm
import os


class LinearMixedModelAnalyzer:
    def __init__(self, excel_file_path, fixed_effects_columns, random_effects_column, target_column):
        self.excel_file_path = excel_file_path
        self.fixed_effects_columns = fixed_effects_columns
        self.random_effects_column = random_effects_column
        self.target_column = target_column
        self.df = None
        self.model = None
        self.result = None

    def load_data(self):
        self.df = pd.read_excel(self.excel_file_path)

    def fit_model(self):
        formula = f'{self.target_column} ~ ' + '+'.join(self.fixed_effects_columns)
        self.model = mixedlm(formula, self.df, groups=self.df[self.random_effects_column])
        self.result = self.model.fit(maxiter=500)  # 设置最大迭代次数为500

    def print_model_summary(self):
        print(self.result.summary())

    def perform_t_test(self):
        print("T 检验结果：")
        tvalues = self.result.tvalues
        pvalues = self.result.pvalues
        for variable in tvalues.index:
            print(f"变量: {variable}")
            print(f"t 值: {tvalues[variable]:.4f}")
            print(f"p 值: {pvalues[variable]:.4f}")
            significance = "显著" if pvalues[variable] < 0.05 else "不显著"
            print(f"显著性: {significance}")
            print("-" * 20)

    def perform_f_test(self, hypothesis):
        print("F 检验结果：")
        try:
            f_test_result = self.result.wald_test(hypothesis)
            f_statistic = f_test_result.statistic.item()  # 提取标量值
            p_value = f_test_result.pvalue.item()  # 提取标量值
            print(f"F 统计量: {f_statistic:.4f}")
            print(f"p 值: {p_value:.4f}")
            significance = "显著" if p_value < 0.05 else "不显著"
            print(f"显著性: {significance}")
        except Exception as e:
            print(f"F 检验失败: {e}")

    def plot_qq_residuals(self, output_path):
        if self.result is None:
            print("请先拟合模型（调用fit_model()）")
            return

        # 确保输出目录存在
        os.makedirs(output_path, exist_ok=True)

        # 提取残差
        residuals = self.result.resid

        # 绘制QQ图
        plt.rcParams['font.family'] = 'SimHei'
        plt.rcParams['axes.unicode_minus'] = False

        fig, ax = plt.subplots(figsize=(8, 6))
        qqplot(
            residuals,
            line='s',  # 添加标准正态分布参考线
            fit=True,  # 拟合残差的均值和标准差
            ax=ax,
            marker='o',  # 点的样式
            color='blue',  # 点的颜色
            alpha=0.7  # 点的透明度
        )
        ax.set_title(f'{self.target_column} 模型残差QQ图', fontsize=12)
        ax.set_xlabel('理论分位数', fontsize=10)
        ax.set_ylabel('残差分位数', fontsize=10)
        plt.grid(alpha=0.3)

        # 保存QQ图
        output_file = os.path.join(output_path, f"{self.target_column}_residuals_qqplot.png")
        plt.savefig(output_file)
        plt.close()

        print(f"残差QQ图已保存到: {output_file}")


def main():
    excel_file_path = r'C:\Users\26790\Desktop\单步处理\附件_1.1_data.xlsx'
    fixed_effects_columns = ['检测孕周', '孕妇BMI', '生产次数']
    random_effects_column = '孕妇代码'
    target_column = 'Y染色体浓度'
    output_plot_path = r'C:\Users\26790\Desktop\Result\Plotting'

    analyzer = LinearMixedModelAnalyzer(excel_file_path, fixed_effects_columns, random_effects_column, target_column)
    analyzer.load_data()
    analyzer.fit_model()
    analyzer.print_model_summary()
    analyzer.perform_t_test()
    hypothesis = '(检测孕周 = 0), (孕妇BMI = 0)'
    analyzer.perform_f_test(hypothesis)
    analyzer.plot_qq_residuals(output_plot_path)  # 绘制并保存QQ图


if __name__ == "__main__":
    main()