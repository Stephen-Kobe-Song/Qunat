import matplotlib
import pandas_datareader as web
import akshare as ak
import numpy as np


from matplotlib import pyplot as plt
matplotlib.use('TkAgg')

print(web.__version__)

# start_date = '2020-01-01'
# end_date = '2020-03-18'
#
# stock = yf.Ticker("601318.SS")
# data = stock.history(start=start_date, end=end_date)
# data = web.data.DataReader('601318.ss', 'yahoo', start_date, end_date)
# data.head()
data = ak.stock_zh_a_hist(symbol="601318", period="daily", start_date="20230101", end_date="20251231")
data['涨跌值'] = data['收盘'] - data['开盘']
data['Signal'] = np.where(data['涨跌值'] > 0, 1, 0)
print(data.head())
plt.figure(figsize=(12, 6))
data['收盘'].plot(linewidth='2', color='k', grid=True)
plt.scatter(data['收盘'].loc[data.Signal == 1].index, data['收盘'][data.Signal == 1], marker='$\u2665$', s=80, c='g')
plt.scatter(data['收盘'].loc[data.Signal == 0].index, data['收盘'][data.Signal == 0], marker='*', s=80, c='r')
plt.savefig('ch1-demo1.png')
plt.show()


"""plt.figure(figsize=(12, 6))
plt.plot(data['日期'], data['收盘'])
plt.title('贵州茅台2021年股价走势')
plt.xlabel('日期')
plt.ylabel('价格')
plt.grid()
# plt.savefig('test.png')
plt.show()"""
"""data.plot(x='日期', y='涨跌额', figsize=(12, 6))
plt.title('China pinan')
plt.ylabel('yuan')
plt.xlabel('date')
plt.grid()
plt.show()"""