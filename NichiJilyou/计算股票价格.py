# 定义需要的变量
name = "夜绯的股票"
stock_price = 19.99
stock_code = "0032032"
# 股票 价格 每日 增长 因子
stock_price_daily_growth_factor = 1.2
grows_days = 7
finally_stock_price = stock_price * stock_price_daily_growth_factor ** grows_days
print(f"公司:{name},股票代码:{stock_code},当前股价{stock_price}")
print("每日增长系数:%.1f,经过%d天的增长后，达到了%.2f"%(stock_price_daily_growth_factor,grows_days,finally_stock_price))
