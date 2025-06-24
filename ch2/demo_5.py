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
    # 设置交易信号
    turtle['buy'] = data['收盘'] > turtle['high']
    turtle['sell'] = data['收盘'] < turtle['low']
    print(turtle.tail())
    # 初始订单数量为0
    turtle['order'] = 0
    # 初始仓位为0
    position = 0

    for k in range(len(turtle)):
        # 当买入信号为true 且仓位为0时，下单买入一手
        if turtle.buy[k] and position == 0:
            turtle.order.values[k] = 1
            # 更新仓位
            position = 1
        # 当卖出信号为true 且持仓时 卖出一手
        elif turtle.sell[k] and position > 0:
            turtle.order.values[k] == -1
            position = 0
    print(turtle.tail(15))

    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data['收盘'], lw=2, label='收盘价')
    plt.plot(data.index, turtle['high'], lw=2, c='b',ls='--', label='上沿')
    plt.plot(data.index, turtle['low'], lw=2, c='r', ls='--', label='下沿')

    buy_points = turtle[turtle['order'] == 1].index
    sell_points = turtle[turtle['order'] == -1].index
    plt.scatter(buy_points, data['收盘'][buy_points], marker='^', s=100,
                c='g', label='买入信号')
    plt.scatter(sell_points, data['收盘'][sell_points], marker='v', s=100,
                c='r', label='卖出信号')

    plt.title('中国平安(601318) 海龟交易策略回测', fontsize=18)
    plt.xlabel('日期', fontsize=14)
    plt.ylabel('价格(元)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # 保存图表并显示
    try:
        plt.savefig('ch2-demo5.png', dpi=300, bbox_inches='tight')
        print("图表已保存为 ch2-demo5.png")
    except Exception as e:
        print(f"保存图表失败: {e}")

    # 尝试显示图表
    try:
        plt.show()
    except Exception as e:
        print(f"无法显示图表: {e}")
        print("若在服务器环境中运行，可通过保存的图片查看结果")
else:
    print("未获取到有效数据")