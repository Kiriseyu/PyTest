import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt

# 假设df['price']为股票价格序列
data = pd.read_csv('stock_prices.csv')
prices = data['price'].values

# 拟合ARIMA模型
model = ARIMA(prices, order=(1,1,1))
model_fit = model.fit()
forecast = model_fit.forecast(steps=10)  # 预测未来10天

# 可视化结果
plt.plot(prices, label='Historical')
plt.plot(range(len(prices), len(prices)+10), forecast, label='Forecast')
plt.legend()
plt.show()
