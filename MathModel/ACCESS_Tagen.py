import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


# 从 Excel 文件中读取数据
excel_file_path = r'C:\Users\26790\Desktop\单步处理\附件_1.1_data.xlsx'
df = pd.read_excel(excel_file_path)

feature_columns = ['检测孕周', '孕妇BMI', '年龄']
target_column = 'Y染色体浓度'

# 划分特征和目标变量
X = df[feature_columns]
y = df[target_column]

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 创建并训练模型
model = LinearRegression()
model.fit(X_train, y_train)

# 在测试集上进行预测
y_pred = model.predict(X_test)

# 评估模型
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# 获取模型系数和截距
beta1, beta2, beta3 = model.coef_
epsilon = model.intercept_

print(f'β1 的值: {beta1.round(4)}')
print(f'β2 的值: {beta2.round(4)}')
print(f'β3 的值: {beta3.round(4)}')
print(f'截距 ε 的值: {epsilon.round(4)}')
# 使用内置的 round 函数来进行四舍五入
print(f'均方误差 (MSE): {round(mse, 4)}')
print(f'决定系数 (R²): {round(r2, 4)}')