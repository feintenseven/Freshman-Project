import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
# 1. 获取当前代码文件所在的“代码”文件夹路径
code_dir = os.path.dirname(os.path.abspath(__file__))
# 2. 定位到上级的“数据”文件夹，拼接彩礼.csv路径（核心修改）
file_path = os.path.join(code_dir, "../数据/result/彩礼.csv")

# 3. 读取数据（和原来一样）
df = pd.read_csv(file_path)

# ====================== 时间数据预处理（仅保留2025年11月） ======================
df['create_time'] = pd.to_datetime(df['create_time'], errors='coerce')

# 筛选2025年11月数据
df_202511 = df[
    (df['create_time'].dt.year == 2025) &
    (df['create_time'].dt.month == 11)
].copy()

# 过滤无效时间数据
df_202511 = df_202511.dropna(subset=['create_time'])

if len(df_202511) == 0:
    print("暂无2025年11月的帖子数据！")
else:
    # 提取时间维度特征（11月内）
    df_202511['day'] = df_202511['create_time'].dt.day  # 日期（1-30）
    df_202511['hour'] = df_202511['create_time'].dt.hour  # 小时
    df_202511['weekday'] = df_202511['create_time'].dt.weekday  # 星期（0=周一）
    df_202511['week'] = df_202511['create_time'].dt.isocalendar().week  # 周数

    # ====================== 11月内发帖量统计 ======================
    # 1. 按日期统计（1-30日）
    daily_posts = df_202511.groupby('day').size().reindex(range(1, 31), fill_value=0).reset_index(name='发帖量')
    daily_posts['日期'] = '11月' + daily_posts['day'].astype(str) + '日'

    # 2. 按小时统计
    hourly_posts = df_202511.groupby('hour').size().reindex(range(0, 24), fill_value=0).reset_index(name='发帖量')

    # 3. 按星期统计
    weekday_mapping = {0: '周一', 1: '周二', 2: '周三', 3: '周四', 4: '周五', 5: '周六', 6: '周日'}
    df_202511['星期'] = df_202511['weekday'].map(weekday_mapping)
    weekday_posts = df_202511.groupby('星期').size().reindex(weekday_mapping.values()).reset_index(name='发帖量')

    # 4. 按周统计（11月包含的周）
    week_posts = df_202511.groupby('week').size().reset_index(name='发帖量')
    week_posts['周数'] = '第' + week_posts['week'].astype(str) + '周'

    # ====================== 输出统计结果 ======================
    print("="*50)
    print("2025年11月帖子发布时间分析")
    print("="*50)
    print(f"11月总发帖量：{len(df_202511)} 条")
    print(f"11月发帖日期范围：{df_202511['create_time'].min()} 至 {df_202511['create_time'].max()}")
    print(f"11月日均发帖量：{len(df_202511)/len(df_202511['day'].unique()):.2f} 条")

    print("\n【11月按日期发帖量】")
    print(daily_posts[daily_posts['发帖量'] > 0])  # 仅显示有发帖的日期

    print("\n【11月按小时发帖量】")
    print(hourly_posts[hourly_posts['发帖量'] > 0].sort_values('hour'))

    print("\n【11月按星期发帖量】")
    print(weekday_posts)

    # ====================== 可视化分析 ======================
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('2025年11月帖子发布时间分布分析', fontsize=18, fontweight='bold')

    # 1. 按日期分布
    ax1 = axes[0, 0]
    ax1.bar(daily_posts['日期'], daily_posts['发帖量'], color='#1f77b4', alpha=0.8)
    ax1.set_title('11月按日期发帖量分布', fontsize=14)
    ax1.set_xlabel('日期')
    ax1.set_ylabel('发帖量')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    # 2. 按小时分布
    ax2 = axes[0, 1]
    ax2.plot(hourly_posts['hour'], hourly_posts['发帖量'], marker='o', linewidth=2, color='#ff7f0e')
    ax2.fill_between(hourly_posts['hour'], hourly_posts['发帖量'], alpha=0.3, color='#ff7f0e')
    ax2.set_title('11月按小时发帖量趋势', fontsize=14)
    ax2.set_xlabel('小时（24小时制）')
    ax2.set_ylabel('发帖量')
    ax2.set_xticks(range(0, 24, 2))
    ax2.grid(linestyle='--', alpha=0.7)

    # 3. 按星期分布
    ax3 = axes[1, 0]
    ax3.bar(weekday_posts['星期'], weekday_posts['发帖量'], color='#2ca02c', alpha=0.8)
    ax3.set_title('11月按星期发帖量分布', fontsize=14)
    ax3.set_xlabel('星期')
    ax3.set_ylabel('发帖量')
    ax3.grid(axis='y', linestyle='--', alpha=0.7)

    # 4. 按周分布
    ax4 = axes[1, 1]
    ax4.pie(week_posts['发帖量'], labels=week_posts['周数'], autopct='%1.1f%%',
            colors=['#d62728', '#9467bd', '#8c564b', '#e377c2'], startangle=90)
    ax4.set_title('11月按周发帖量占比', fontsize=14)

    plt.tight_layout()
    plt.savefig("./result/2025年11月发帖时间分析.png", dpi=300, bbox_inches='tight')

    # ====================== 峰值分析 ======================
    peak_day = daily_posts.loc[daily_posts['发帖量'].idxmax()]
    peak_hour = hourly_posts.loc[hourly_posts['发帖量'].idxmax()]
    peak_weekday = weekday_posts.loc[weekday_posts['发帖量'].idxmax()]

    print("\n" + "="*50)
    print("11月发帖量峰值分析")
    print("="*50)
    print(f"峰值日期：{peak_day['日期']}（{peak_day['发帖量']}条）")
    print(f"峰值时段：{peak_hour['hour']}点（{peak_hour['发帖量']}条）")
    print(f"峰值星期：{peak_weekday['星期']}（{peak_weekday['发帖量']}条）")

    plt.show()