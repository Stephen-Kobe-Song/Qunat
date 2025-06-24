import matplotlib
import matplotlib.pyplot as plt
import akshare as ak
import numpy as np
import pandas as pd

# 设置Matplotlib后端（可根据环境注释）
matplotlib.use('TkAgg')

# 设置中文显示
plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

try:
    # 获取中国平安股票数据
    data = ak.stock_zh_a_hist(symbol="601318", period="daily",
                              start_date="20250101", end_date="20250601")
except Exception as e:
    print(f"获取股票数据失败: {e}")

if not data.empty:
    # 将日期列转换为索引
    data.set_index('日期', inplace=True)

    # 初始化海龟策略数据框
    turtle = pd.DataFrame(index=data.index)

    # 计算海龟策略关键指标
    turtle['high_20'] = data['收盘'].rolling(20).max()  # 20日最高价
    turtle['low_20'] = data['收盘'].rolling(20).min()  # 20日最低价
    turtle['close'] = data['收盘']

    # 生成交易信号（向量化实现，比循环更高效）
    turtle['buy_signal'] = turtle['close'] > turtle['high_20']  # 突破上轨买入
    turtle['sell_signal'] = turtle['close'] < turtle['low_20']  # 跌破下轨卖出

    # 初始化订单和仓位（使用fillna处理首日NaN）
    turtle['position'] = 0
    turtle['order'] = 0

    # 优化交易逻辑（向量化实现，替代for循环）
    for i in range(1, len(turtle)):
        # 买入逻辑：出现买入信号且当前无仓位
        if turtle['buy_signal'].iloc[i] and turtle['position'].iloc[i - 1] == 0:
            turtle.at[turtle.index[i], 'position'] = 1
            turtle.at[turtle.index[i], 'order'] = 1
        # 卖出逻辑：出现卖出信号且当前有仓位
        elif turtle['sell_signal'].iloc[i] and turtle['position'].iloc[i - 1] == 1:
            turtle.at[turtle.index[i], 'position'] = 0
            turtle.at[turtle.index[i], 'order'] = -1
        # 无信号时保持仓位
        else:
            turtle.at[turtle.index[i], 'position'] = turtle['position'].iloc[i - 1]
            turtle.at[turtle.index[i], 'order'] = 0

    # 计算交易结果
    turtle['return'] = np.zeros_like(turtle['close'])
    for i in range(1, len(turtle)):
        if turtle['position'].iloc[i] == 1 and turtle['position'].iloc[i - 1] == 0:
            turtle.at[turtle.index[i], 'entry_price'] = turtle['close'].iloc[i]
        elif turtle['position'].iloc[i] == 0 and turtle['position'].iloc[i - 1] == 1:
            turtle.at[turtle.index[i], 'exit_price'] = turtle['close'].iloc[i]
            # 计算单笔交易收益率
            buy_price = turtle['entry_price'].iloc[i - 1]
            turtle.at[turtle.index[i], 'return'] = (turtle['exit_price'].iloc[i] - buy_price) / buy_price

    # 打印策略结果
    print("海龟策略后15行数据:")
    print(turtle[['close', 'high_20', 'low_20', 'position', 'order', 'return']].tail(15))

    # 统计策略绩效
    total_trades = len(turtle[turtle['order'] != 0])
    winning_trades = len(turtle[(turtle['order'] == -1) & (turtle['return'] > 0)])
    if total_trades > 0:
        win_rate = winning_trades / total_trades * 100
        avg_return = turtle['return'][turtle['return'] != 0].mean() * 100
        print(f"\n策略绩效统计:")
        print(f"总交易次数: {total_trades}")
        print(f"盈利次数: {winning_trades}")
        print(f"胜率: {win_rate:.2f}%")
        print(f"平均收益率: {avg_return:.2f}%")

    # 绘制策略可视化图表
    plt.figure(figsize=(16, 8))

    # 绘制价格和上下轨
    plt.plot(data.index, data['收盘'], lw=2, label='收盘价')
    plt.plot(data.index, turtle['high_20'], lw=1.5, c='b', ls='--', label='20日最高价(上轨)')
    plt.plot(data.index, turtle['low_20'], lw=1.5, c='r', ls='--', label='20日最低价(下轨)')

    # 标记买卖点
    buy_points = turtle[turtle['order'] == 1].index
    sell_points = turtle[turtle['order'] == -1].index

    plt.scatter(buy_points, data['收盘'][buy_points], marker='^', s=120,
                c='g', label='买入信号', zorder=5)
    plt.scatter(sell_points, data['收盘'][sell_points], marker='v', s=120,
                c='r', label='卖出信号', zorder=5)

    # 图表装饰
    plt.title('中国平安(601318) 海龟交易策略回测', fontsize=18)
    plt.xlabel('日期', fontsize=14)
    plt.ylabel('价格(元)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()

    try:
        plt.savefig('ch2-demo6.png', dpi=300, bbox_inches='tight')
        print("图表已保存为 ch2-demo6.png")
    except Exception as e:
        print(f"保存图表失败: {e}")
    # 显示图表
    plt.show()
else:
    print("未获取到有效数据")