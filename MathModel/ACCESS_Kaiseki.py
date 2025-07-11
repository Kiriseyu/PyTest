import pandas as pd
import matplotlib.pyplot as plt
import os

plt.rcParams['font.family'] = 'SimHei'
plt.rcParams['axes.unicode_minus'] = False

class DA:
    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir
        self.deta = None

    def rodo(self):
        try:
            self.deta = pd.read_excel(self.input_file, sheet_name="Sheet1")
            print("数据加载成功。")
        except Exception as e:
            print(f"加载数据时发生错误：{e}")

    def generate_descriptive_stats(self):
        if self.deta is None:
            print("尚未加载数据，请先加载数据。")
            return

        stats = self.deta.describe().transpose()
        stats['偏度'] = self.deta.skew()
        stats['峰度'] = self.deta.kurtosis()

        stats_output_path = os.path.join(self.output_dir, "描述性统计.xlsx")
        stats.to_excel(stats_output_path, index=True)
        print(f"描述性统计已保存至 {stats_output_path}")

        return stats

    def plot_descriptive_stats_table(self, stats):
        if stats is None:
            print("尚未生成统计量，请先生成统计量。")
            return

        os.makedirs(self.output_dir, exist_ok=True)
        transposed_stats = stats.transpose()

        plt.figure(figsize=(15, 10))
        ax = plt.subplot(111)
        ax.axis('off')

        col_widths = [0.2] + [0.12] * len(transposed_stats.columns)

        table = plt.table(
            cellText=transposed_stats.values.round(4),
            colLabels=transposed_stats.columns,
            rowLabels=transposed_stats.index,
            cellLoc='center',
            loc='center',
            colWidths=col_widths
        )

        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.2)

        for (row, col), cell in table.get_celld().items():
            if row == 0:
                continue
            if col == -1:
                cell.set_text_props(ha='left')

        table_path = os.path.join(self.output_dir, "描述性统计表.png")
        plt.tight_layout()
        plt.savefig(table_path, bbox_inches='tight', dpi=300)
        plt.close()

        print(f"描述性统计表已保存至 {table_path}")

    def main(self):
        self.rodo()
        stats = self.generate_descriptive_stats()
        self.plot_descriptive_stats_table(stats)

if __name__ == "__main__":
    input_file_path = "输入文件路径"
    output_dir_path = "输出文件夹路径"

    analyzer = DA(input_file_path, output_dir_path)
    analyzer.main()