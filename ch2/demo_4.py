import matplotlib
import matplotlib.pyplot as plt
import akshare as ak
import numpy as np
import pandas as pd
matplotlib.use('TkAgg')
# 设置Matplotlib后端（根据环境选择，可注释此行让系统自动选择）
# matplotlib.use('TkAgg')

# 设置中文显示
plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

try:
    data = ak.stock_zh_a_hist(symbol="601318", period="daily",
                              start_date="20250101", end_date="20250601")
except Exception as e:
    print(f"获取股票数据失败: {e}")
    # 生成示例数据用于测试
    dates = pd.date_range(start='2025-01-01', end='2025-06-01', freq='B')
    np.random.seed(42)
    close_prices = 50 + np.random.randn(len(dates)).cumsum() * 0.5
    data = pd.DataFrame({
        '日期': dates,
        '收盘': close_prices
    })

if not data.empty:
    # 初始化现金资产
    initial_cash = 20000

    # 将日期列转换为索引
    data.set_index('日期', inplace=True)

    # 新建策略数据表
    strategic = pd.DataFrame(index=data.index)

    # 计算技术指标
    strategic['avg_5'] = data['收盘'].rolling(5).mean()
    strategic['avg_10'] = data['收盘'].rolling(10).mean()

    # 生成交易信号
    strategic['signal'] = np.where(strategic['avg_5'] > strategic['avg_10'], 1, 0)
    strategic['order'] = strategic['signal'].diff()

    # 初始化持仓数据（每次交易100股）
    positions = pd.DataFrame(index=strategic.index).fillna(0)
    positions['stock'] = strategic['signal'] * 100  # 1信号对应100股，0信号对应0股

    # 初始化投资组合数据
    portfolio = pd.DataFrame(index=data.index)

    # 计算持仓市值
    portfolio['stock_value'] = positions.multiply(data['收盘'], axis=0)

    # 计算交易订单（每日持仓变化）
    order = positions.diff()

    # 计算现金余额（考虑交易成本，此处简化为无手续费）
    portfolio['cash'] = initial_cash - (order.multiply(data['收盘'], axis=0)).cumsum()

    # 计算总资产
    portfolio['total'] = portfolio['cash'] + portfolio['stock_value']

    # 计算收益率
    portfolio['return'] = portfolio['total'] / initial_cash - 1

    print("投资组合后10行数据:")
    print(portfolio.tail(10))

    # 绘制图表
    plt.figure(figsize=(14, 7))

    # 绘制总资产和持仓价值
    plt.plot(data.index, portfolio['total'], lw=2, c='r', label='总资产')
    plt.plot(data.index, portfolio['stock_value'], lw=2, c='b', ls='--', label='持仓总价值')

    # 标记买卖点
    buy_points = strategic[strategic['order'] == 1].index
    sell_points = strategic[strategic['order'] == -1].index

    plt.scatter(buy_points, portfolio['total'][buy_points], marker='^', s=100,
                c='g', label='买入信号')
    plt.scatter(sell_points, portfolio['total'][sell_points], marker='v', s=100,
                c='r', label='卖出信号')

    # 图表装饰
    plt.title('中国平安(601318) 双均线交易策略回测', fontsize=16)
    plt.xlabel('日期', fontsize=14)
    plt.ylabel('金额(元)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # 保存图表并显示
    try:
        plt.savefig('ch2-demo4.png', dpi=300, bbox_inches='tight')
        print("图表已保存为 ch2-demo4.png")
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