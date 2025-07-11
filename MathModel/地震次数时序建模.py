import pandas as pd
# import os
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf  # 自相关系数计算与画图函数
from statsmodels.graphics.tsaplots import plot_pacf  # 偏自相关系计算与画图数函数
from statsmodels.stats.diagnostic import acorr_ljungbox as lb_test  # 白噪声检验之LB检验
from statsmodels.tsa.stattools import adfuller  # 单位根检验
from statsmodels.tsa.ar_model import AutoReg  # 自回归AR函数
# from statsmodels.sandbox.regression.predstd import wls_prediction_std  # 自回归拟合的标准偏差、置信区间

plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
plt.rcParams['axes.unicode_minus'] = False  # 正常显示正负号
plt.rcParams.update({'figure.figsize': (8, 6), 'figure.dpi': 100})  # 设置图片大小

# 1.数据预处理
# 读取数据时显式指定频率（假设数据是年度数据）
data_quakes = pd.read_excel('C:/Users/26790/Desktop/数学建模/时序模型/earthquake.xlsx', parse_dates=['year'])
data_quakes.set_index('year', inplace=True)  # 此时数据表为DataFrame格式
data_quakes = data_quakes.asfreq('YS-JAN')

# 画时序图
fig, ax = plt.subplots()
ax.plot(data_quakes.index, data_quakes.quakes)
ax.set(xlabel='年份', ylabel='地震数', title='年地震次数时序图')
plt.show()

# 计算自相关系数和偏自相关系数
plot_acf(data_quakes.quakes)  # 生成自相关系数图
plot_pacf(data_quakes.quakes)  # 生成偏自关系数图
plt.show()
# 生成adf检验结果，单位根检验
unitroot_result = adfuller(data_quakes.quakes)  # 单位根检验
critical_value = pd.DataFrame.from_dict(unitroot_result[4], orient='index')
critical_value.columns = ['临界值']
print('ADF统计量: %.3f' % unitroot_result[0])
print('p value: %.3f' % unitroot_result[1])
print('滞后阶数: %d' % unitroot_result[2])
print('观测值数量: %d' % unitroot_result[3])
print(critical_value)

# 白噪声LB检验
quakesLB = lb_test(data_quakes.quakes, lags=None, boxpierce=True)
plt.plot(quakesLB, label=['lb_stat', 'lb_pvalue', 'bp_stat', 'bp_pvalue'])  # 白噪声LB检验
plt.title('白噪声检验之LB、BP统计')
plt.legend()
plt.show()
print('白噪声检验之LB与BP统计量')
print(lb_test(data_quakes.quakes, lags=None, boxpierce=True))
# 2. 模型识别
# 3. 1阶AR模型参数估计与结果
model = AutoReg(data_quakes.quakes, lags=1)
model_fit = model.fit()
print(model_fit.summary())

# 绘图：原始数据点，AR模型拟合曲线
## prstd, ivLow, ivUp = wls_prediction_std(model_fit)  # 返回标准偏差和置信区间
plt.plot(data_quakes.index, data_quakes.quakes, 'r', label='Original Value')
plt.plot(data_quakes.index[1:], model_fit.fittedvalues, 'b', label='AR Model Value')
# 上述data_quakes.year[2:]中的[1:]是因为在model_fit中比data_quakes少了前两项第0，由回归阶数1确定
# plt.plot(ivUp, '--',color='orange', label='ConfInt')  # 置信区间 上限
# plt.plot(ivLow, '--',color='orange')
plt.legend()
plt.show()
# 4.模型显著性检验
# 模型检验-残差分析
resid = model_fit.resid
plot_acf(resid)  # 生成残差自相关系数图
plot_pacf(resid)  # 生成残差偏自关系数图
plt.show()
unitroot_resid = adfuller(resid)  # 生成adf检验结果，单位根检验
print('The ADF Statistic of resid: %f' % unitroot_resid[0])
print('The p value of resid: %f' % unitroot_resid[1])
print(unitroot_resid)
residLB = lb_test(resid, lags=None, boxpierce=False)
plt.plot(residLB, label=['lb_stat', 'lb_pvalue'])  # 残差白噪声LB检验
plt.title('残差白噪声检验之LB统计')
plt.legend()
plt.show()
print('白噪声检验之LB统计量')
print(lb_test(resid, lags=None, boxpierce=False))
# 5。模型优化
# 收集、计算不同滞后阶数p下的模型AIC，BIC值并做出大小比较
p_values = range(0, 6)
aicbic = pd.DataFrame(columns=['p', 'aic', 'bic'])
for p in p_values:
    try:
        model = AutoReg(data_quakes, lags=p)
        results = model.fit()
        aicbic.loc[len(aicbic)] = [int(p), results.aic, results.bic]
    except Exception as e:
        print(f"p={p}时发生错误:{e}")
        continue

print('各滞后阶数p下的AIC与BIC值')
print(aicbic)
aic_idxmin = aicbic['aic'].idxmin(axis=0)
bic_idxmin = aicbic['bic'].idxmin(axis=0)
print('AIC最小值与对应阶数p:  ')
print(aicbic.iloc[aic_idxmin])
print('BIC最小值与对应阶数p:  ')
print(aicbic.iloc[bic_idxmin])

# 模型优化，取p=3
mmodel = AutoReg(data_quakes.quakes, lags=3)
mmodel_fit = mmodel.fit()
print('优化后的模型')
print(mmodel_fit.summary())

#  对优化模型AR（3）的显著性检验-残差分析
resid = mmodel_fit.resid
plot_acf(resid)  # 生成残差自相关系数图
plot_pacf(resid)  # 生成残差偏自关系数图
plt.show()
unitroot_resid = adfuller(resid)  # 生成adf检验结果，单位根检验
print('ADF Statistic of resid: %f' % unitroot_resid[0])
print('p value of resid: %f' % unitroot_resid[1])
print(unitroot_resid)
residLB = lb_test(resid, lags=None, boxpierce=False)
plt.plot(residLB, label=['lb_stat', 'lb_pvalue'])  # 残差白噪声LB检验
plt.title('残差白噪声检验之LB统计')
plt.legend()
plt.show()
print('优化模型AR(3)白噪声检验之LB统计量')
print(residLB)
# 6。利用模型预测
# 预测未来5年，即从1999年到2003年的地震次数
forecast_years = 5
forecast = mmodel_fit.forecast(steps=forecast_years).round(0)  # 进行预测，不保留小数
# 保存预测结果并绘图：

# 生成预测的年份
future_years = np.arange(1999, 1999 + forecast_years)

# 创建包含拟合值和预测值的新DataFrame
future_quakes = pd.DataFrame({'year': future_years, 'quakes': forecast})
future_quakes.set_index('year', inplace=True)
# 将预测值添加到拟合数据中
mmodel_fit = pd.DataFrame({'year': data_quakes.index[3:], 'quakes': mmodel_fit.fittedvalues})  # 转化为DataFrame格式
mmodel_fit.set_index('year', inplace=True)
df_forecasted = pd.concat([mmodel_fit, future_quakes])

# 绘制实际值和预测值的对比图
plt.figure(figsize=(10, 6))
plt.plot(df_forecasted.index, df_forecasted.quakes, label='Forecasted Quakes', marker='*')
plt.plot(data_quakes.index, data_quakes.quakes, label='Actual Quakes', linestyle='--', marker='o')
plt.title('Quakes Forecast for 1999-2003 (AR(3))')
plt.xlabel('Year')
plt.ylabel('quakes')
plt.legend()
plt.grid(True)
plt.show()

# 输出未来5年的预测值，
print("预测的1999-2003年地震次数:")
print(future_quakes.round(0))
