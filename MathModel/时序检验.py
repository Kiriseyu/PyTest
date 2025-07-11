import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf  # 自相关系数函数
from statsmodels.graphics.tsaplots import plot_pacf  # w偏自相关系数函数
from statsmodels.tsa.stattools import adfuller  # 单位根检验

temperature = r'C:\Users\26790\Desktop\数学建模\时序模型\maxtem.xlsx'
milk = r'C:\Users\26790\Desktop\数学建模\时序模型\naiyield.xlsx'
sha = r'C:\Users\26790\Desktop\数学建模\时序模型\shayield.xlsx'

# 读取数据
data_tem = pd.read_excel(temperature, parse_dates=True)
data_milk = pd.read_excel(milk, parse_dates=True)
data_sha = pd.read_excel(sha, parse_dates=True)

# 绘制时序图
plt.plot(data_sha.year, data_sha.shayield)
plt.title('ShaYield Over Time')
plt.xlabel('year')
plt.ylabel('shayield')
plt.show()

plt.plot(data_milk.monthyear, data_milk.milkyield)
plt.title('MilkYield Over Time')
plt.xlabel('month-year')
plt.ylabel('milkyield')
plt.show()

plt.plot(data_tem.year, data_tem.tem)
plt.title('Temperature Over Year')
plt.xlabel('year')
plt.ylabel('tem')
plt.show()

# 绘制相关图与自相关图
plt.rcParams.update({'figure.figsize': (8, 6), 'figure.dpi': 100})  # 设置图片大小
plot_acf(data_sha.shayield)  # 生成自相关图
plot_pacf(data_sha.shayield)  # 生成偏自相关图
plot_acf(data_milk.milkyield)
plot_pacf(data_milk.milkyield)
plot_acf(data_tem.tem)
plot_pacf(data_tem.tem)
plt.show()

# 进行单位根检验（ADF检验）
# 例1 纱产量
unitroot_result = adfuller(data_sha.shayield)  # 单位根检验
critical_value = pd.DataFrame.from_dict(unitroot_result[4], orient='index')
critical_value.columns = ['临界值']
print('ADF统计量: %.3f' % unitroot_result[0])
print('p value: %.3f' % unitroot_result[1])
print('滞后阶数: %d' % unitroot_result[2])
print('观测值数量: %d' % unitroot_result[3])
print(critical_value)

# 例2 牛奶产量
unitroot_result = adfuller(data_milk.milkyield)
print('ADF Statistic: %.3f' % unitroot_result[0])
print('p value: %.3f' % unitroot_result[1])
# 例3 年最高气温
unitroot_result = adfuller(data_tem.tem)
critical_value = pd.DataFrame.from_dict(unitroot_result[4], orient='index')
critical_value.columns = ['临界值']
print('ADF统计量: %.3f' % unitroot_result[0])
print('p value: %.3f' % unitroot_result[1])
print('滞后阶数: %d' % unitroot_result[2])
print('观测值数量: %d' % unitroot_result[3])
print(critical_value)
