import matplotlib
import akshare as ak
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


matplotlib.use('TkAgg')

data = ak.stock_zh_a_hist(symbol="601318", period="daily", start_date="20250101", end_date="20250601")
# print(data.head())
# 只保留原始数据中的日期index
data_signal = pd.DataFrame(index=data.index)
data_signal['price'] = data['收盘']
data_signal['diff'] = data_signal['price'].diff()
# 增加diff字段后，第一行会出现空值 用0填充
data_signal = data_signal.fillna(0.0)
# 设置交易信号，0卖出1买入
data_signal['signal'] = np.where(data_signal['diff'] >= 0, 0, 1)
data_signal['order'] = data_signal['signal'].diff() * 100
# 初始现金资产
initial_cash = 20000.0
# 股票交易的市值
data_signal['stock'] = data_signal['order'] * (data_signal['price'])
# 交易后的现金值
data_signal['cash'] = initial_cash - data_signal['stock'].cumsum()
# 股票的市值加上现金就是总资产
data_signal['total'] = data_signal['stock'] + data_signal['cash']

print(data_signal.head())

plt.figure(figsize=(12, 6))
plt.plot(data_signal['total'], label='total value')
plt.plot(data_signal['order'].cumsum() * data_signal['price'], '--', label='stock value')
plt.grid()
plt.legend(loc='center right')
plt.savefig('ch2-demo1.png')
plt.show()
