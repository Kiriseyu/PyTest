# 时序预测模型对比笔记
from sklearn.preprocessing import MinMaxScaler

models_comparison = {
    "传统统计模型": {
        "ARIMA": {
            "适用场景": "- 数据量小、无外部特征\n- 季节性/趋势明显且稳定\n- 短期预测（如月度销售）",
            "优势": "- 理论成熟，参数解释性强\n- 计算效率高",
            "局限": "- 无法捕捉非线性关系\n- 需手动处理季节性/趋势"
        },
        "指数平滑法(Holt-Winters)": {
            "适用场景": "- 数据无显著趋势/季节性\n- 快速迭代需求（如库存预测）",
            "优势": "- 模型简单，易调参\n- 短期预测效果好",
            "局限": "- 仅适合简单线性模式\n- 长期预测偏差大"
        }
    },
    "机器学习模型": {
        "LSTM": {
            "适用场景": "- 复杂非线性关系（如股票价格、能源负荷）\n- 多变量输入（如温度+负荷）",
            "优势": "- 拟合能力强\n- 支持长期依赖",
            "局限": "- 计算资源需求高\n- 模型可解释性差"
        },
        "Prophet": {
            "适用场景": "- 显著季节性/节假日效应（如电商销量、网络流量）\n- 业务快速迭代需求",
            "优势": "- 自动化建模\n- 可解释性强\n- 支持节假日调整",
            "局限": "- 对非线性模式拟合能力弱\n- 需预设趋势形状"
        }
    },
    "核心差异总结": {
        "结构": "传统模型（线性） vs 机器学习（非线性/分解）",
        "数据假设": "传统需平稳 vs 机器学习适应非平稳",
        "资源需求": "传统（低） vs 机器学习（高）",
        "解释性": "传统（强） vs 机器学习（弱）"
    },
    "选择建议": {
        "简单场景": "优先传统模型（ARIMA/ETS）",
        "复杂场景": "优先机器学习（LSTM/Prophet）",
        "混合方案": "Prophet分解趋势 + LSTM捕捉残差非线性"
    }
}
# ARIMA模型
# 通过差分（I）将非平稳序列转化为平稳序列，结合自回归（AR）和移动平均（MA）捕捉线性关系。
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd

# 加载数
data = pd.read_csv('data.csv', index_col='date', parse_dates=True)
# 拟合ARIMA模型（p=1, d=1, q=1）
model = ARIMA(data, order=(1,1,1))
results = model.fit()
# 预测未来5期
forecast = results.get_forecast(steps=5)
print(forecast.summary())


# 指数平滑法(Holt-Winters)
# 通过加权平均历史数据，近期数据权重更高，支持趋势和季节性扩展。
from statsmodels.tsa.holtwinters import ExponentialSmoothing
# 拟合Holt-Winters模型（加法季节性）
model = ExponentialSmoothing(data, seasonal='add', seasonal_periods=12)
results = model.fit()
# 预测未来12期
forecast = results.forecast(12)
print(forecast)


# LSTM模型
# 通过门控机制（输入门、遗忘门、输出门）解决长期依赖问题，捕捉非线性关系。
from keras.models import Sequential
from keras.layers import LSTM, Dense
import numpy as np
# 数据预处理（标准化并创建滑动窗口）
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(data)
# 创建滑动窗口（窗口大小=60）
X, y = [], []
for i in range(60, len(scaled_data)):
    X.append(scaled_data[i-60:i, 0])
    y.append(scaled_data[i, 0])
X, y = np.array(X), np.array(y)
X = np.reshape(X, (X.shape[0], X.shape[1], 1))
# 构建LSTM模型
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)))
model.add(LSTM(50))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mse')
# 训练模型
model.fit(X, y, epochs=100, batch_size=32)
# 预测未来值
future_input = scaled_data[-60:]
future_input = np.reshape(future_input, (1, 60, 1))
predicted_value = model.predict(future_input)


# Prophet模型
# 将时间序列分解为趋势、季节性、节假日效应，支持自动化调参和可解释性分析。
from fbprophet import Prophet
import pandas as pd
# 加载数据并格式化
data = pd.read_csv('data.csv')
data['ds'] = pd.to_datetime(data['date'])
data['y'] = data['value']
# 定义节假日（可选）
holidays = pd.DataFrame({
    'holiday': 'event',
    'ds': pd.to_datetime(['2023-12-25', '2024-01-01']),
    'lower_window': 0,
    'upper_window': 1,
})
# 拟合Prophet模型
model = Prophet(holidays=holidays, seasonality_mode='multiplicative')
model.fit(data)
# 预测未来30天
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])