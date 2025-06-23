import matplotlib
import akshare as ak
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
matplotlib.use('TkAgg')
# 设置中文显示
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]


data = ak.stock_zh_a_hist(symbol="601318", period="daily", start_date="20250101", end_date="20250601")

# print(data.head())
period = 10
# 设置空裂变存储十天的价格
avg_10 = []
# 设置列表存储十天的均值
avg_value = []
for price in data['收盘']:
    avg_10.append(price)
    # 当列表中超过十天的数据，删除第一条
    if len(avg_10) > period:
        del avg_10[0]
    # 将十天的均价放入列表中
    avg_value.append(np.mean(avg_10))
data = data.assign(avg_10=pd.Series(avg_value, index=data.index))
print(data.head())

plt.figure(figsize=(12, 6))
plt.plot(data['日期'], data['收盘'], lw=2, c='k', label='收盘价')
plt.plot(data['日期'], data['avg_10'], lw=2, c='b', label=f'{period}日移动平均线')

plt.title('中国平安(601318) 收盘价与移动平均线', fontsize=16)
plt.xlabel('日期', fontsize=12)
plt.ylabel('价格', fontsize=12)
# 设置x轴日期显示间隔(每5个交易日显示一次)
plt.xticks(data['日期'][::5], rotation=45)
plt.legend(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
"""plt.legend()
plt.grid()"""
plt.tight_layout()
plt.savefig('ch2-demo2.png')
plt.show()