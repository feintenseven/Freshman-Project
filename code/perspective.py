import pandas as pd
import matplotlib.pyplot as plt
import re
from collections import defaultdict

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 加载数据
file_path = './result/彩礼.csv'
df = pd.read_csv(file_path)
df = df.fillna({'text': '', 'title': '', 'gender': 0})

# 性别映射
gender_mapping = {0: '未知', 1: '男性', 2: '女性'}
df['gender_mapped'] = df['gender'].map(gender_mapping)

# ====================== 定义彩礼态度关键词 ======================
attitude_keywords = {
    '支持': [
        '彩礼应该给', '支持彩礼', '彩礼是传统', '彩礼合理', '彩礼体现诚意',
        '适量彩礼', '彩礼有必要', '彩礼是仪式', '彩礼量力而行'
    ],
    '一般': [
        '无所谓', '看情况', '都行', '随便', '中立', '看双方协商',
        '都可以', '没意见', '视情况而定'
    ],
    '不支持': [
        '反对彩礼', '彩礼没必要', '取消彩礼', '彩礼是陋习', '抵制彩礼',
        '彩礼太高', '减少彩礼', '彩礼害人', '零彩礼'
    ]
}


# ====================== 态度分类函数 ======================
def classify_c彩礼_attitude(text):
    text = str(text).lower()
    attitude_scores = defaultdict(int)

    # 匹配各态度关键词
    for attitude, keywords in attitude_keywords.items():
        for keyword in keywords:
            if keyword.lower() in text:
                attitude_scores[attitude] += 1

    # 返回得分最高的态度（无匹配则为"一般"）
    if attitude_scores:
        return max(attitude_scores, key=attitude_scores.get)
    else:
        # 兜底规则：通过情感词判断
        support_words = ['支持', '应该', '合理', '传统', '必要']
        oppose_words = ['反对', '取消', '陋习', '没必要', '抵制']

        support_count = sum(1 for word in support_words if word in text)
        oppose_count = sum(1 for word in oppose_words if word in text)

        if support_count > oppose_count:
            return '支持'
        elif oppose_count > support_count:
            return '不支持'
        else:
            return '一般'


# 合并标题和内容进行态度分析
df['full_text'] = df['title'].astype(str) + ' ' + df['text'].astype(str)
df['attitude'] = df['full_text'].apply(classify_c彩礼_attitude)

# ====================== 分性别统计态度分布 ======================
# 1. 整体态度分布
total_attitude = df['attitude'].value_counts()
total_attitude_ratio = df['attitude'].value_counts(normalize=True) * 100

# 2. 男性态度分布
male_df = df[df['gender_mapped'] == '男性']
male_attitude = male_df['attitude'].value_counts()
male_attitude_ratio = male_df['attitude'].value_counts(normalize=True) * 100

# 3. 女性态度分布
female_df = df[df['gender_mapped'] == '女性']
female_attitude = female_df['attitude'].value_counts()
female_attitude_ratio = female_df['attitude'].value_counts(normalize=True) * 100

# 整合统计结果（确保索引一致）
attitude_categories = ['支持', '一般', '不支持']
attitude_stats = pd.DataFrame({
    '整体数量': [total_attitude.get(cat, 0) for cat in attitude_categories],
    '整体占比(%)': [round(total_attitude_ratio.get(cat, 0), 2) for cat in attitude_categories],
    '男性数量': [male_attitude.get(cat, 0) for cat in attitude_categories],
    '男性占比(%)': [round(male_attitude_ratio.get(cat, 0), 2) for cat in attitude_categories],
    '女性数量': [female_attitude.get(cat, 0) for cat in attitude_categories],
    '女性占比(%)': [round(female_attitude_ratio.get(cat, 0), 2) for cat in attitude_categories]
}, index=attitude_categories)

# ====================== 输出统计结果 ======================
print("=" * 80)
print("不同性别对彩礼的态度分布统计")
print("=" * 80)
print(attitude_stats)

print(f"\n整体样本量：{len(df)} 条")
print(f"男性样本量：{len(male_df)} 条")
print(f"女性样本量：{len(female_df)} 条")

# ====================== 可视化分析 ======================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('不同性别对彩礼的态度分布对比', fontsize=16, fontweight='bold')

# 颜色配置
colors = ['#2ca02c', '#ff7f0e', '#d62728']  # 支持-绿色，一般-橙色，不支持-红色

# 1. 数量对比柱状图
x = attitude_categories
width = 0.25
ax1.bar([i - width for i in range(len(x))], attitude_stats['整体数量'], width, label='整体', color=colors, alpha=0.8)
ax1.bar(range(len(x)), attitude_stats['男性数量'], width, label='男性', color=colors, alpha=0.6)
ax1.bar([i + width for i in range(len(x))], attitude_stats['女性数量'], width, label='女性', color=colors, alpha=0.4)

ax1.set_title('态度分布数量对比', fontsize=14)
ax1.set_xlabel('态度倾向')
ax1.set_ylabel('帖子数量')
ax1.set_xticks(range(len(x)))
ax1.set_xticklabels(x)
ax1.legend()
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# 2. 占比对比柱状图
ax2.bar([i - width for i in range(len(x))], attitude_stats['整体占比(%)'], width, label='整体', color=colors, alpha=0.8)
ax2.bar(range(len(x)), attitude_stats['男性占比(%)'], width, label='男性', color=colors, alpha=0.6)
ax2.bar([i + width for i in range(len(x))], attitude_stats['女性占比(%)'], width, label='女性', color=colors, alpha=0.4)

ax2.set_title('态度分布占比对比(%)', fontsize=14)
ax2.set_xlabel('态度倾向')
ax2.set_ylabel('占比(%)')
ax2.set_xticks(range(len(x)))
ax2.set_xticklabels(x)
ax2.legend()
ax2.grid(axis='y', linestyle='--', alpha=0.7)

# 添加百分比标签
for i, container in enumerate(ax2.containers):
    ax2.bar_label(container, fmt='%.1f%%', fontsize=8)

plt.tight_layout()
plt.savefig("./result/性别-彩礼态度对比分析.png", dpi=300, bbox_inches='tight')

# ====================== 额外分析：未知性别群体对比 ======================
unknown_df = df[df['gender_mapped'] == '未知']
unknown_attitude = unknown_df['attitude'].value_counts()
unknown_attitude_ratio = unknown_df['attitude'].value_counts(normalize=True) * 100

print("\n" + "=" * 80)
print("未知性别群体态度分布")
print("=" * 80)
for cat in attitude_categories:
    print(f"{cat}：{unknown_attitude.get(cat, 0)} 条（{unknown_attitude_ratio.get(cat, 0):.2f}%）")

plt.show()