import matplotlib
import matplotlib.pyplot as plt
import akshare as ak
import numpy as np
import pandas as pd
import os
from datetime import datetime

# 设置Matplotlib后端（可根据环境注释）
matplotlib.use('TkAgg')

# 设置中文显示
plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题


def get_stock_data():
    save_dir = "stock_data"
    file_name = "pingan_stock_20250101_20250601.csv"
    file_path = os.path.join(save_dir, file_name)

    # 检查文件是否存在
    if os.path.exists(file_path):
        print(f"发现已有数据文件: {file_path}")
        try:
            df = pd.read_csv(file_path)
            print(f"成功从本地读取数据，包含 {len(df)} 行记录")
            return df
        except Exception as e:
            print(f"读取文件失败: {e}")
            print("将尝试重新下载数据...")

    # 文件不存在或读取失败，执行下载
    try:
        print("开始下载股票数据...")
        data = ak.stock_zh_a_hist(
            symbol="601318",
            period="daily",
            start_date="20200101",
            end_date="20250601"
        )

        if data is None or data.empty:
            raise ValueError("下载的数据为空")

        # 确保目录存在
        os.makedirs(save_dir, exist_ok=True)

        # 保存数据
        data.to_csv(file_path, index=False, encoding="utf-8-sig")
        print(f"数据已成功保存到: {file_path}")
        print(f"下载的数据包含 {len(data)} 行记录")
        return data

    except Exception as e:
        print(f"获取或保存股票数据失败: {e}")
        return None


if __name__ == "__main__":
    df = get_stock_data()
    if df is not None:
        print("\n\t数据前几行内容:")
        print(df.head().to_csv(sep='\t', na_rep='nan'))
