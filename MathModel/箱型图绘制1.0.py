import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 设置图片清晰度
plt.rcParams['figure.dpi'] = 300

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
# 定义文件路径列表
file_paths = ['C:/Users/26790/Desktop/boxFiles/高钾-风化.xlsx',
              'C:/Users/26790/Desktop/boxFiles/高钾-无风化.xlsx',
              'C:/Users/26790/Desktop/boxFiles/铅钡-风化.xlsx',
              'C:/Users/26790/Desktop/boxFiles/铅钡-无风化.xlsx']

# 用于存储所有数据的列表
all_data = []

# 遍历文件路径列表
for file_path in file_paths:
    try:
        # 读取 Excel 文件
        excel_file = pd.ExcelFile(file_path)

        # 获取所有表名
        sheet_names = excel_file.sheet_names

        # 遍历不同工作表
        for sheet_name in sheet_names:
            try:
                # 获取当前工作表的数据
                df = excel_file.parse(sheet_name)

                # 获取绘图所需的数据，即化学物质含量相关列
                chemical_columns = df.columns[4:]
                all_data.append(df[chemical_columns])
            except Exception as e:
                print(f'在解析文件 {file_path} 的工作表 {sheet_name} 时出现错误: {e}')
    except FileNotFoundError:
        print(f'文件 {file_path} 未找到。')
    except pd.errors.ParserError:
        print(f'文件 {file_path} 格式错误，无法解析。')
    except Exception as e:
        print(f'处理文件 {file_path} 时出现其他错误: {e}')

# 将所有数据合并成一个 DataFrame
combined_data = pd.concat(all_data, ignore_index=True)

# 创建画布
plt.figure(figsize=(15, 10))

# 绘制箱型图
sns.boxplot(data=combined_data)

# 设置图形标题和坐标轴标签
plt.title('各化学物质含量箱型图')
plt.xlabel('化学物质')
plt.ylabel('含量')
plt.xticks(rotation=90)

# 显示图形
plt.show()