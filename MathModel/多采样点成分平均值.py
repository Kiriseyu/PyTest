import os
import pandas as pd
from datetime import datetime

def main():
    # 配置参数
    input_file = "./result/cleaned_with_clr.xlsx"  # 输入文件路径
    output_dir = "result"  # 输出文件夹
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "averaged_clr_data.xlsx")  # 输出文件路径

    # 日志文件路径
    log_file = os.path.join(output_dir, "data_processing.log")

    # 设置日志
    log_lines = []

    def log(msg):
        """记录日志信息"""
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{t}] {msg}"
        print(line)
        log_lines.append(line)

    try:
        # 检查输入文件是否存在
        if not os.path.exists(input_file):
            log(f"错误：输入文件 {input_file} 不存在。")
            raise FileNotFoundError(f"输入文件 {input_file} 不存在。")

        # 读取 Excel 文件
        log(f"开始读取文件: {input_file}")
        df = pd.read_excel(input_file)
        log(f"成功读取文件: {input_file}, 数据行数: {len(df)}")

        # 动态匹配 clr 处理后的化学成分列（假设列名包含 'CLR_' 前缀）
        clr_columns = [col for col in df.columns if col.startswith("CLR_")]

        # 检查是否存在 clr 列
        if not clr_columns:
            log("错误：未找到以 'CLR_' 开头的列。")
            raise ValueError("未找到以 'CLR_' 开头的列。")

        # 按文物编号分组并计算平均值
        log("开始计算同一文物编号的平均值...")
        averaged_df = df.groupby("文物编号")[clr_columns].mean().reset_index()
        log(f"计算完成, 得到 {len(averaged_df)} 条平均记录")

        # 保存结果到新的 Excel 文件
        log(f"开始保存结果到文件: {output_file}")
        averaged_df.to_excel(output_file, index=False, sheet_name="Averaged_CLR_Data")
        log(f"结果成功保存到文件: {output_file}")

        # 保存日志
        log(f"开始保存日志到文件: {log_file}")
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines))
        log(f"日志成功保存到文件: {log_file}")

    except Exception as e:
        log(f"处理过程中发生错误: {str(e)}")
        raise  # 如果需要可以让异常继续抛出

if __name__ == "__main__":
    main()