import os
import pandas as pd
from scipy.stats import chi2_contingency
# from datetime import datetime

# 加载数据
result_path = "./InputFiles"
file_name = "表单1.xlsx"
file_path = os.path.join(result_path, file_name)
df = pd.read_excel(file_path)

# log生成
log_lines = []
def log(msg):
    # t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{msg}"
    print(line)
    log_lines.append(line)

# 数据编码统一化
df['表面风化'] = df['表面风化'].map({'风化': 1, '无风化': 2})
df['类型'] = df['类型'].map({'高钾': 1, '铅钡': 2})

# 处理颜色缺失值，将缺失值视为一个单独的类别（编码为9）
df['颜色'] = df['颜色'].fillna(9)

# 创建列联表
# 表面风化 vs 类型（2x2表）
contingency_table_type = pd.crosstab(df['表面风化'], df['类型'])

# 表面风化 vs 纹饰（2x3表）
contingency_table_decoration = pd.crosstab(df['表面风化'], df['纹饰'])

# 表面风化 vs 颜色（2x9表，包括“未知”类别）
contingency_table_color = pd.crosstab(df['表面风化'], df['颜色'])

# 卡方检验
# 对表面风化与类型进行卡方检验
chi2_type, p_type, dof_type, expected_type = chi2_contingency(contingency_table_type)

# 对表面风化与纹饰进行卡方检验
chi2_decoration, p_decoration, dof_decoration, expected_decoration = chi2_contingency(contingency_table_decoration)

# 对表面风化与颜色进行卡方检验
chi2_color, p_color, dof_color, expected_color = chi2_contingency(contingency_table_color)

# 检查期望频数
log("表面风化与类型期望频数：")
log(expected_type)
log("\n表面风化与纹饰期望频数：")
log(expected_decoration)
log("\n表面风化与颜色期望频数：")
log(expected_color)

# 输出卡方检验结果
log(f"\n表面风化与类型卡方检验结果：卡方值={chi2_type}, p值={p_type}")
log(f"表面风化与纹饰卡方检验结果：卡方值={chi2_decoration}, p值={p_decoration}")
log(f"表面风化与颜色卡方检验结果：卡方值={chi2_color}, p值={p_color}")

# 写文件
log_file_name = "卡方检验_log.txt"
try:
    os.remove(log_file_name)
except FileNotFoundError:
    pass
log_file_path = os.path.join(result_path, log_file_name)
with open(log_file_path, 'w', encoding='utf-8') as f:
    for line in log_lines:
        f.write(line + '\n')
