import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from scipy.stats import pearsonr

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 读取数据并预处理
df = pd.read_csv('./result/彩礼.csv')
df = df.fillna({
    'view': 0, 'reply': 0, 'share': 0, 'agree': 0, 'disagree': 0,
    'text': '', 'title': ''
})

# 计算综合热度
df['热度'] = df['view'] * 3 + df['reply'] * 5 + df['share'] * 3 + df['agree'] + df['disagree']

# 2. 按热度分位数分组
# 计算分位数阈值
q10 = df['热度'].quantile(0.9)    # 前10%高热度阈值
q40 = df['热度'].quantile(0.4)    # 中等热度下限
q60 = df['热度'].quantile(0.6)    # 中等热度上限
q20 = df['热度'].quantile(0.2)    # 后20%低热度阈值

# 定义分组函数
def heat_group(heat):
    if heat >= q10:
        return '高热度（前10%）'
    elif q40 <= heat < q60:
        return '中等热度（40%-60%）'
    elif heat <= q20:
        return '低热度（后20%）'
    else:
        return '其他'

df['热度分组'] = df['热度'].apply(heat_group)

# 只保留三组有效数据
df_grouped = df[df['热度分组'].isin(['高热度（前10%）', '中等热度（40%-60%）', '低热度（后20%）'])]

# ------------------------------------------------------------------------------
# 3. 各组核心指标对比
# ------------------------------------------------------------------------------
# 3.1 互动指标均值对比
interaction_cols = ['view', 'reply', 'share', 'agree', 'disagree', '热度']
group_interaction = df_grouped.groupby('热度分组')[interaction_cols].mean().round(2)
print("=== 不同热度分组的互动指标均值对比 ===")
print(group_interaction)

# 可视化互动指标对比（柱状图）
fig, ax = plt.subplots(figsize=(12, 8))
group_interaction.T.plot(kind='bar', ax=ax, width=0.7)
ax.set_title('不同热度分组的互动指标对比', fontsize=14)
ax.set_xlabel('互动指标', fontsize=12)
ax.set_ylabel('均值', fontsize=12)
ax.legend(title='热度分组', fontsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('./result/热度分组互动指标对比.png', dpi=300, bbox_inches='tight')
plt.close()

# 3.2 帖子长度对比
df_grouped['帖子长度'] = df_grouped['text'].astype(str).apply(len)
group_length = df_grouped.groupby('热度分组')['帖子长度'].agg(['mean', 'median']).round(2)
print("\n=== 不同热度分组的帖子长度对比 ===")
print(group_length)

# 可视化帖子长度对比
fig, ax = plt.subplots(figsize=(10, 6))
group_length['mean'].plot(kind='bar', color=['#1f77b4', '#ff7f0e', '#2ca02c'], ax=ax)
ax.set_title('不同热度分组的平均帖子长度对比', fontsize=14)
ax.set_xlabel('热度分组', fontsize=12)
ax.set_ylabel('平均字符数', fontsize=12)
ax.grid(axis='y', linestyle='--', alpha=0.7)
for i, v in enumerate(group_length['mean']):
    ax.text(i, v + 10, f'{int(v)}', ha='center', fontsize=10)
plt.savefig('./result/热度分组帖子长度对比.png', dpi=300, bbox_inches='tight')
plt.close()

# 3.3 语气特征对比（疑问/感叹语气占比）
# 定义语气判断函数
def has_question(text):
    return 1 if re.search(r'[？?]', str(text)) else 0

def has_exclamation(text):
    return 1 if re.search(r'[！!]', str(text)) else 0

# 计算语气特征
df_grouped['含疑问语气'] = (df_grouped['title'] + df_grouped['text']).astype(str).apply(has_question)
df_grouped['含感叹语气'] = (df_grouped['title'] + df_grouped['text']).astype(str).apply(has_exclamation)

# 统计各组语气占比
group_tone = df_grouped.groupby('热度分组')[['含疑问语气', '含感叹语气']].mean().round(3) * 100
print("\n=== 不同热度分组的语气特征占比（%） ===")
print(group_tone)

# 可视化语气特征对比
fig, ax = plt.subplots(figsize=(10, 6))
group_tone.plot(kind='bar', ax=ax, width=0.7, color=['#ff7f0e', '#d62728'])
ax.set_title('不同热度分组的语气特征占比', fontsize=14)
ax.set_xlabel('热度分组', fontsize=12)
ax.set_ylabel('占比（%）', fontsize=12)
ax.legend(['含疑问语气', '含感叹语气'], fontsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.7)
for i, col in enumerate(group_tone.columns):
    for j, v in enumerate(group_tone[col]):
        ax.text(j + (i-0.5)*0.3, v + 1, f'{v}%', ha='center', fontsize=9)
plt.savefig('./result/热度分组语气特征对比.png', dpi=300, bbox_inches='tight')
plt.close()

# 3.4 用户特征对比（等级、性别、VIP）
user_cols = ['level', 'glevel', 'is_vip']
group_user = df_grouped.groupby('热度分组')[user_cols].agg({
    'level': 'mean',
    'glevel': 'mean',
    'is_vip': lambda x: (x == 1).mean() * 100  # VIP占比
}).round(2)
group_user.rename(columns={'is_vip': 'VIP占比（%）'}, inplace=True)
print("\n=== 不同热度分组的用户特征对比 ===")
print(group_user)

# 可视化用户特征对比
fig, ax = plt.subplots(figsize=(10, 6))
group_user[['level', 'glevel']].plot(kind='bar', ax=ax, width=0.7, color=['#1f77b4', '#2ca02c'])
ax2 = ax.twinx()
group_user['VIP占比（%）'].plot(kind='line', ax=ax2, marker='o', color='red', linewidth=2)
ax.set_title('不同热度分组的用户特征对比', fontsize=14)
ax.set_xlabel('热度分组', fontsize=12)
ax.set_ylabel('平均等级', fontsize=12)
ax2.set_ylabel('VIP占比（%）', fontsize=12, color='red')
ax.legend(['用户等级', '贴吧等级'], fontsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('./result/热度分组用户特征对比.png', dpi=300, bbox_inches='tight')
plt.close()

# ------------------------------------------------------------------------------
# 4. 输出对比结果到CSV
# ------------------------------------------------------------------------------
# 合并所有对比结果
comparison_result = pd.concat([
    group_interaction.add_prefix('互动_'),
    group_length.add_prefix('长度_'),
    group_tone.add_prefix('语气_'),
    group_user.add_prefix('用户_')
], axis=1)

comparison_result.to_csv('./result/热度分组对比分析.csv', encoding='utf-8-sig')
print("\n热度分组对比分析结果已保存至./result/热度分组对比分析.csv")