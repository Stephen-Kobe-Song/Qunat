import matplotlib
import matplotlib.pyplot as plt
import akshare as ak
import numpy as np
import pandas as pd
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import locale
locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')

# 设置Matplotlib后端（可根据环境注释）
matplotlib.use('TkAgg')
# 设置中文显示
plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题


def get_stock_data():
    """获取并缓存股票数据，优先读取本地文件"""
    save_dir = "stock_data"
    file_name = "pingan_stock_20200101_20250601.csv"
    file_path = os.path.join(save_dir, file_name)

    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, parse_dates=['日期'])
            print(f"本地读取成功，共 {len(df)} 条记录 | {file_path}")
            return df
        except Exception as e:
            print(f"本地文件损坏: {e}，将重新下载")

    # 下载逻辑
    try:
        print("开始下载股票数据...")
        data = ak.stock_zh_a_hist(
            symbol="601318",
            period="daily",
            start_date="20200101",
            end_date="20250601"
        )
        if data is None or data.empty:
            raise ValueError("下载数据为空")

        os.makedirs(save_dir, exist_ok=True)
        data.to_csv(file_path, index=False, encoding="utf-8-sig")
        print(f"数据已保存: {file_path} | 共 {len(data)} 条记录")
        return data

    except Exception as e:
        print(f"数据获取失败: {e}")
        return None


def prepare_classification_data(df, test_size=0.2, random_state=42):
    """准备分类模型数据，包含特征工程、标准化、数据集划分"""
    # 特征工程
    df['Open-Close'] = df['开盘'] - df['收盘']
    df['High-Low'] = df['最高'] - df['最低']
    df['target'] = np.where(df['收盘'].shift(-1) > df['收盘'], 1, -1)

    # 数据清洗
    df = df.dropna().reset_index(drop=True)  # 重置索引避免后续切片问题
    if len(df) < 10:  # 确保有足够数据建模
        raise ValueError("有效数据不足，请检查数据源")

    # 特征与标签
    X = df[['Open-Close', 'High-Low']]
    y = df['target']

    # 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 划分数据集（时间序列不打乱）
    split_idx = int(len(X) * (1 - test_size))
    X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    return X_train, X_test, y_train, y_test, scaler, X, y, df


def optimize_knn_model(X_train, y_train):
    """网格搜索优化 KNN 参数，找到最佳 K 值"""
    param_grid = {'n_neighbors': range(5, 100, 5)}  # K 值搜索范围
    grid_search = GridSearchCV(
        KNeighborsClassifier(),
        param_grid,
        cv=5,
        scoring='accuracy',
        n_jobs=1
    )
    grid_search.fit(X_train, y_train)
    print(f"🔍 最佳参数: {grid_search.best_params_} | 验证集准确率: {grid_search.best_score_:.4f}")
    return grid_search.best_estimator_


def calculate_returns(df):
    """计算基准收益和策略收益，修复 shift 错位问题"""
    df['Return'] = np.log(df['收盘'] / df['收盘'].shift(1))
    df['Return'] = df['Return'].fillna(0)  # 填充首日收益为0
    return df


def strategy_returns(df, split_idx):
    """计算策略收益（修正 shift 逻辑）"""
    df['Strategy_Return'] = df['Return'] * df['Predict_Signal'].shift(1)
    df['Strategy_Return'] = df['Strategy_Return'].fillna(0)  # 填充首日策略收益
    return df[split_idx:]['Strategy_Return'].cumsum() * 100


def benchmark_returns(df, split_idx):
    """计算基准收益"""
    return df[split_idx:]['Return'].cumsum() * 100


def plot_performance(benchmark, strategy, symbol):
    """可视化收益对比，支持保存图片"""
    plt.figure(figsize=(14, 7))
    plt.plot(benchmark, '--', label=f'{symbol} 基准收益')
    plt.plot(strategy, label='策略收益')
    plt.title(f'{symbol} 基准收益 vs 策略收益对比', fontsize=16)
    plt.xlabel('交易日期', fontsize=12)
    plt.ylabel('累计收益 (%)', fontsize=12)
    plt.legend()
    plt.grid(alpha=0.6, linestyle='--')
    plt.tight_layout()
    plt.savefig('ch3-demo1.png')  # 保存图片
    plt.show()


if __name__ == "__main__":
    # 1. 获取数据
    df = get_stock_data()
    if df is None:
        exit(1)

    # 2. 数据预处理与特征工程
    try:
        X_train, X_test, y_train, y_test, scaler, X, y, df = prepare_classification_data(df)
    except ValueError as e:
        print(f"数据准备失败: {e}")
        exit(1)

    # 3. 模型训练（网格搜索优化）
    best_knn = optimize_knn_model(X_train, y_train)
    best_knn.fit(X_train, y_train)

    # 4. 模型评估
    print("\n模型评估报告:")
    y_pred = best_knn.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=['下跌', '上涨']))

    # 5. 生成预测信号
    df['Predict_Signal'] = best_knn.predict(scaler.transform(X))  # 用训练好的 scaler 转换

    # 6. 收益计算
    df = calculate_returns(df)
    split_idx = len(X_train)
    benchmark = benchmark_returns(df, split_idx)
    strategy = strategy_returns(df, split_idx)

    # 7. 可视化
    plot_performance(benchmark, strategy, '中国平安')

    # 8. 额外输出：策略 vs 基准最终收益
    print(f"\n最终收益对比:")
    print(f"基准收益: {benchmark.iloc[-1]:.2f}%")
    print(f"策略收益: {strategy.iloc[-1]:.2f}%")