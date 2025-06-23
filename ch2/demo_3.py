import matplotlib
import matplotlib.pyplot as plt
import akshare as ak
import numpy as np
import pandas as pd
matplotlib.use('TkAgg')
# 设置中文显示
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 获取股票数据
try:
    data = ak.stock_zh_a_hist(symbol="601318", period="daily",
                              start_date="20250101", end_date="20250601")
except Exception as e:
    print(f"获取股票数据失败: {e}")
    # 可添加备选数据源或示例数据

# 数据预处理
if not data.empty:
    # 将日期列转换为索引并确保与strategic表对齐
    data.set_index('日期', inplace=True)

    # 新建策略数据表
    strategic = pd.DataFrame(index=data.index)

    # 计算技术指标
    strategic['avg_5'] = data['收盘'].rolling(5).mean()
    strategic['avg_10'] = data['收盘'].rolling(10).mean()

    # 生成交易信号
    strategic['signal'] = np.where(strategic['avg_5'] > strategic['avg_10'], 1, 0)
    strategic['order'] = strategic['signal'].diff()

    print(strategic.tail(10))

    # 绘制图表
    plt.figure(figsize=(14, 7))

    # 绘制价格和均线
    plt.plot(data.index, data['收盘'], lw=2, c='k', label='收盘价')
    plt.plot(data.index, strategic['avg_5'], lw=1.5, c='b', label='5日均线')
    plt.plot(data.index, strategic['avg_10'], lw=1.5, c='r', label='10日均线')

    # 标记买卖点
    buy_points = strategic[strategic['order'] == 1].index
    sell_points = strategic[strategic['order'] == -1].index

    plt.scatter(buy_points, data['收盘'][buy_points], marker='^', s=100,
                c='r', label='买入信号')
    plt.scatter(sell_points, data['收盘'][sell_points], marker='v', s=100,
                c='g', label='卖出信号')

    # 图表装饰
    plt.title('中国平安(601318) 双均线交易策略', fontsize=16)
    plt.xlabel('日期', fontsize=14)
    plt.ylabel('价格', fontsize=14)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.tight_layout()

    # 保存图表并显示
    try:
        plt.savefig('ch2-demo3.png', dpi=300, bbox_inches='tight')
        print("图表已保存为 ch2-demo3.png")
    except Exception as e:
        print(f"保存图表失败: {e}")

    # 尝试显示图表（可能在无头环境中失败）
    try:
        plt.show()
    except Exception as e:
        print(f"无法显示图表: {e}")
        print("若在服务器环境中运行，可通过保存的图片查看结果")
else:
    print("未获取到有效数据")