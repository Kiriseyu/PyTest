import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import logging


class ExcelCorrelationAnalysis:
    def __init__(self, file_path, output_file_path, output_image_path):
        self.file_path = file_path
        self.output_file_path = output_file_path
        self.output_image_path = output_image_path
        self.excel_file = pd.ExcelFile(self.file_path)
        self.sheet_names = self.excel_file.sheet_names
        os.makedirs(self.output_file_path, exist_ok=True)
        os.makedirs(self.output_image_path, exist_ok=True)
        # 配置日志记录器
        logging.basicConfig(filename=os.path.join(output_file_path, 'correlation_analysis.log'),
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def get_sheet_data(self, sheet_name):
        return self.excel_file.parse(sheet_name)

    def calculate_pearson_corr(self, df):
        numeric_df = df.select_dtypes(include='number')
        return numeric_df.corr().round(2)

    def save_corr_matrix_to_console(self, corr_matrix, sheet_name):
        print(f'sheet表名为 {sheet_name} 的相关系数矩阵:')
        print(corr_matrix)

    def save_corr_matrix_to_log(self, corr_matrix, sheet_name):
        logging.info(f'sheet表名为 {sheet_name} 的相关系数矩阵:')
        logging.info(corr_matrix.to_csv(sep='\t', na_rep='nan'))

    def plot_corr_heatmap(self, corr_matrix, sheet_name):
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
        plt.title(f'{sheet_name} 相关系数矩阵热力图')
        output_path = os.path.join(self.output_image_path, f'{sheet_name}_corr_heatmap.png')
        plt.savefig(output_path)
        plt.close()

    def run_analysis(self):
        for sheet_name in self.sheet_names:
            df = self.get_sheet_data(sheet_name)
            corr_matrix = self.calculate_pearson_corr(df)
            # 输出到控制台
            self.save_corr_matrix_to_console(corr_matrix, sheet_name)
            # 输出到日志文件
            # self.save_corr_matrix_to_log(corr_matrix, sheet_name)

if __name__ == "__main__":
    file_path = r'C:\Users\26790\Desktop\单步处理\附件_1.1_data.xlsx'
    output_file_path = r'C:\Users\26790\Desktop\Result\AnalysisResult'
    output_image_path = r'C:\Users\26790\Desktop\Result\Plotting'
    analysis = ExcelCorrelationAnalysis(file_path, output_file_path, output_image_path)
    analysis.run_analysis()
