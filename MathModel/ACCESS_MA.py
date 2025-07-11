import pandas as pd
import numpy as np
from statsmodels.stats.outliers_influence import variance_inflation_factor
import logging
import os


# 日志设置函数
def setup_logging(log_path):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 读取Excel文件函数，可自定义列
def read_excel(file_path, sheet_names, columns=None):
    data = {}
    logging.info("开始读取Excel文件...")
    try:
        for sheet_name in sheet_names:
            if columns:
                df = pd.read_excel(file_path, sheet_name=sheet_name, usecols=columns)
            else:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            data[sheet_name] = df
        logging.info(f"成功读取工作表: {sheet_names}。")
    except Exception as e:
        logging.error(f"读取Excel失败: {e}")
        raise
    return data


# 合并数据函数
def concat_data(data):
    return pd.concat(list(data.values()), ignore_index=True)


# 筛选数值型变量并剔除常数列函数
def preprocess_numeric_data(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    df_numeric = df[numeric_cols].dropna(axis=1, how='all')  # 剔除全为NaN的列
    df_numeric = df_numeric.loc[:, df_numeric.nunique() > 1]  # 剔除常数列
    return df_numeric


# 计算VIF函数
def calculate_vif(df):
    vif_data = pd.DataFrame()
    vif_data["feature"] = df.columns
    vif_data["VIF"] = [variance_inflation_factor(df.values, i) for i in range(df.shape[1])]
    return vif_data


# 保存结果函数
def save_result(result, output_path):
    try:
        result.to_excel(output_path, index=False)
        logging.info(f"VIF结果已保存至: {output_path}")
    except Exception as e:
        logging.error(f"保存结果失败: {e}")
        raise


def main():
    # 日志设置
    log_path = r"C:\Users\26790\Desktop\CleanedLog\multicollinearity.log"
    setup_logging(log_path)

    # 路径设置
    file_path = r"C:\Users\26790\Desktop\单步处理\附件_1.1_zscore.xlsx"
    output_dir = r"C:\Users\26790\Desktop\Result\AnalysisResult"
    os.makedirs(output_dir, exist_ok=True)

    # 自定义要读取的列
    selected_columns = ['年龄', '孕妇BMI', '检测孕周','生产次数' ]
    sheet_names = ["Sheet1"]
    data = read_excel(file_path, sheet_names, selected_columns)

    # 合并数据
    df_all = concat_data(data)

    # 筛选数值型变量并剔除常数列
    df_numeric = preprocess_numeric_data(df_all)

    if df_numeric.empty:
        logging.warning("没有有效的数值型变量用于VIF分析。")
        raise ValueError("没有有效的数值型变量用于VIF分析。")

    # 计算VIF
    vif_result = calculate_vif(df_numeric)

    # 保存结果
    output_path = os.path.join(output_dir, "VIF_Multicollinearity_Result.xlsx")
    save_result(vif_result, output_path)

    # 控制台打印
    print("多重共线性分析完成，VIF结果如下：")
    print(vif_result)

if __name__ == "__main__":
    main()
