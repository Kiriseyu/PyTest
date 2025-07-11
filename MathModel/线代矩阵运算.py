# 加减法
# 行列数相同时#规则：对应元素相加相减
import numpy as np

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 0], [1, 2]])
print("A+B=\n", np.add(A, B))
print("A-B=\n", np.subtract(A, B))
# 数乘
# 数与矩阵每个元素相乘
K = 3
A = np.array([[3, 6], [9, 12]])
print("KA=\n", np.dot(K, A))
# 乘法
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
print("AB=\n", np.dot(A, B))
# 转置
A = np.array([[1, 3, 5], [2, 4, 6], [7, 8, 9]])
print("A ^ T = \n", np.transpose(A))
# 逆矩阵
# 方阵且行列式不为零
# AB = BA = I, 则B为A的逆矩阵
A = np.array([[2, 1], [1, 1]])
print("A^{-1}=\n", np.linalg.inv(A))
# 线性方程组求解
# 解方程组{2x+y=5
#         x+y=3
# 增广矩阵：2 1|5
#         1 1|3
A = np.array([[2, 1], [1, 1]])
b = np.array([5, 3])
print(np.linalg.solve(A, b))
# 特征值与特征向量
# 解特征方程det(A-λI)=0
# A=[2 3
#    3 -6]
# 特征方程λ^2+4λ-21=0
# 求特征值和特征向量
A = np.array([[2, 3], [3, -6]])
EigenValues, EigenVectors = np.linalg.eig(A)
print("特征值", EigenValues)
print("特征向量", EigenVectors)

## 概率论
# 离散型随机变量//二项分布
# 抛硬币10次，正面次数X∼B(10,0.5)，期望E(X)=5，方差Var(X)=2.5。
from scipy.stats import binom

n, p = 10, 0.5
X = binom(n, p)
print("期望", X.mean())
print("方差", X.var())
# 连续型随机变量//正态分布、均匀分布
from scipy.stats import norm

mu = 70
sigma = 10
X = norm(mu, sigma)
print("期望", X.mean())
print("方差", X.var())

# 样本均值与样本方差
data = np.random.normal(70, 10, 1000)
print("样本均值", np.mean(data))
print("样本方差", np.var(data))

# 大数定律与中心极限定理
# 大数：样本均值趋近于总体均值
# 中心极限：样本均值近似正态分布
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

font_path = "C:/Windows/Fonts/STXINWEI.TTF"
hwxw_font = FontProperties(fname=font_path)
sample_means = [np.mean(np.random.exponential(1, 100))]
plt.hist(sample_means, bins=30, edgecolor='black')
plt.title("样本均值的分布(中心极限定理)", fontproperties=hwxw_font)
plt.xlabel("样本均值", fontproperties=hwxw_font)
plt.ylabel("频数", fontproperties=hwxw_font)
plt.show()

# 使用py对csv文件进行数据清洗和数据分析
import pandas as pd


def load_and_clean_csv(file_path, encoding='utf-8'):
    try:
        df = pd.read_csv(file_path, encoding=encoding)
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='gbk')
    # 基础清洗
    df.columns = ['c1', 'c2', 'c3']  # 重命名列
    df.dropna(inplace=True)  # 删除空值
    df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
    return df


csv_df = load_and_clean_csv("data.csv")
tsv_df = pd.read_csv("data.tsv", sep='\t')  # 单独处理TSV

# 读取Excel文件
excel_single_sheet = pd.read_excel("data.xlsx", sheet_name='Sheet1')
excel_all_sheets = pd.read_excel('data.xlsx', sheet_name=None)  # 返回字典

# 导入json文件
df = pd.read_json('data.json')
# 导入数据库
import sqlite3

cn = sqlite3.connect('database.db')
sl = pd.read_sql('SELECT * FROM table_name', cn)

from sqlalchemy import create_engine


engine = create_engine('mysql://user:password@localhost/db_name')
sle = pd.read_sql('SELECT * FROM table_name', engine)

# TXT文件
dr = pd.read_csv('data.txt', sep='|')  # |为分隔符

# 数据清洗
# 查看缺失值
print(df.isnull().sum())
# 删除缺失值
df_cleaned = df.dropna()  # 删除缺失值的行
df_cleaned = df.dropna(subset=['col1', 'col2'])  # 删除指定列缺失值
# 填充缺失值
df_filled = df.fillna(0)  # 用0填充
df_filled = df.fillna(df.mean())   # 用均值填充数值列
df_filled = df.fillna({'col1': 'Unknown', 'col2': 0})  # 不同列不同填充方式
