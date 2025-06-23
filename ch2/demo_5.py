import matplotlib
import matplotlib.pyplot as plt
import akshare as ak
import numpy as np
import pandas as pd
matplotlib.use('TkAgg')

# 设置中文显示
plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

try:
    data = ak.stock_zh_a_hist(symbol="601318", period="daily",
                              start_date="20250101", end_date="20250601")
except Exception as e:
    print(f"获取股票数据失败: {e}")

if not data.empty:
    # 将日期列转换为索引
    data.set_index('日期', inplace=True)
    # 创建新的数据域表
    turtle = pd.DataFrame(index=data.index)
    # 统计过去20天内股票的最高价
    turtle['high'] = data['收盘'].shift(1).rolling(20).max()
    # 统计过去20天内股票的最低价
    turtle['low'] = data['收盘'].shift(1).rolling(20).min()
else:
    print("未获取到有效数据")