import pandas as pd
import matplotlib.pyplot as plt
import re

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

# ====================== 修复正则表达式 ======================
# 感性特征：感叹号、问号（连续/单个）
emotional_punctuations = r'!{1,}|！{1,}|\?{1,}|？{1,}'  # 修复重复匹配问题
emotional_words = ['啊', '呀', '哇', '哦', '呢', '嘛', '吧', '咯', '唉', '哼', '天哪', '卧槽', '气死', '哭', '笑', '烦']

# 理性特征：句号、分号、引号（修复正则语法）
rational_punctuations = r'\。{1,}|;{1,}|；{1,}|"{1,}|"{2,}|\'{1,}|\'{2,}'  # 修复""+问题
rational_words = ['数据', '统计', '根据', '研究', '分析', '客观', '理性', '事实', '依据', '具体', '举例']


# ====================== 语气特征提取函数（增加异常处理） ======================
def analyze_emotional_features(text):
    try:
        text = str(text).strip()
        features = {
            'emotional_punc_count': 0,
            'rational_punc_count': 0,
            'emotional_word_count': 0,
            'rational_word_count': 0,
            'text_length': max(len(text), 1),  # 避免除以0
            'emotional_score': 0,
            'rational_score': 0,
            'tendency': '中性'
        }

        # 匹配感性标点
        if text:
            features['emotional_punc_count'] = len(re.findall(emotional_punctuations, text))

        # 匹配理性标点
        if text:
            features['rational_punc_count'] = len(re.findall(rational_punctuations, text))

        # 匹配感性词汇
        features['emotional_word_count'] = sum(1 for word in emotional_words if word in text)

        # 匹配理性词汇
        features['rational_word_count'] = sum(1 for word in rational_words if word in text)

        # 计算得分（归一化）
        features['emotional_score'] = (features['emotional_punc_count'] * 2 + features['emotional_word_count']) / \
                                      features['text_length'] * 100
        features['rational_score'] = (features['rational_punc_count'] * 2 + features['rational_word_count']) / features[
            'text_length'] * 100

        # 判断倾向
        if features['emotional_score'] > features['rational_score'] + 0.5:
            features['tendency'] = '感性'
        elif features['rational_score'] > features['emotional_score'] + 0.5:
            features['tendency'] = '理性'

        return features

    except Exception as e:
        print(f"处理文本时出错: {e}")
        return {
            'emotional_punc_count': 0,
            'rational_punc_count': 0,
            'emotional_word_count': 0,
            'rational_word_count': 0,
            'text_length': 1,
            'emotional_score': 0,
            'rational_score': 0,
            'tendency': '中性'
        }


# 合并标题和内容分析
df['full_text'] = df['title'].astype(str) + ' ' + df['text'].astype(str)

# 提取语气特征
feature_results = df['full_text'].apply(analyze_emotional_features)
feature_df = pd.DataFrame(feature_results.tolist())

# 合并到原数据
df = pd.concat([df, feature_df], axis=1)

# ====================== 统计分析 ======================
# 整体语气倾向分布
tendency_counts = df['tendency'].value_counts()
tendency_ratio = df['tendency'].value_counts(normalize=True) * 100

# 不同性别的语气倾向分布
gender_tendency = pd.crosstab(df['gender_mapped'], df['tendency'])
gender_tendency_ratio = pd.crosstab(df['gender_mapped'], df['tendency'], normalize='index') * 100

# 输出结果
print("=" * 50)
print("文本语气倾向（理性/感性）统计")
print("=" * 50)
print("【整体语气倾向分布】")
for tendency, count in tendency_counts.items():
    print(f"{tendency}：{count} 条（{tendency_ratio[tendency]:.2f}%）")

print("\n【不同性别的语气倾向分布（百分比%）】")
print(gender_tendency_ratio.round(2))

# ====================== 可视化 ======================
# 1. 整体语气倾向饼图
plt.figure(figsize=(8, 6))
colors = ['#FF69B4', '#4169E1', '#2ca02c']  # 感性-粉色，理性-蓝色，中性-绿色
# 确保颜色与类别匹配
pie_labels = tendency_counts.index.tolist()
pie_colors = [colors[pie_labels.index(t)] if t in pie_labels else '#d3d3d3' for t in ['感性', '理性', '中性']]
pie_colors = [c for c, t in zip(pie_colors, ['感性', '理性', '中性']) if t in pie_labels]

wedges, texts, autotexts = plt.pie(
    tendency_counts,
    labels=tendency_counts.index,
    autopct='%1.1f%%',
    colors=pie_colors,
    startangle=90,
    explode=(0.05, 0.05, 0)[:len(tendency_counts)]
)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
plt.title('整体文本语气倾向分布', fontsize=14)
plt.savefig("./result/整体语气倾向分布.png", dpi=300, bbox_inches='tight')

# 2. 不同性别的语气倾向堆叠柱状图
plt.figure(figsize=(10, 6))
gender_tendency_ratio.plot(
    kind='bar',
    stacked=True,
    color=colors[:len(gender_tendency_ratio.columns)],
    ax=plt.gca()
)
plt.title('不同性别的语气倾向分布（%）', fontsize=14)
plt.xlabel('性别', fontsize=12)
plt.ylabel('占比（%）', fontsize=12)
plt.legend(title='语气倾向')
plt.grid(axis='y', linestyle='--', alpha=0.3)

# 添加百分比标签
for i, gender in enumerate(gender_tendency_ratio.index):
    cumulative = 0
    for j, tendency in enumerate(gender_tendency_ratio.columns):
        value = gender_tendency_ratio.iloc[i, j]
        if value > 5:
            plt.text(i, cumulative + value / 2, f'{value:.1f}%',
                     ha='center', va='center', fontsize=9, color='white', fontweight='bold')
        cumulative += value

plt.tight_layout()
plt.savefig("./result/性别-语气倾向分布.png", dpi=300, bbox_inches='tight')

# 3. 感性/理性得分分布箱线图
plt.figure(figsize=(10, 6))
df[['emotional_score', 'rational_score']].plot(
    kind='box',
    vert=False,
    patch_artist=True,
    boxprops=dict(facecolor='lightblue'),
    ax=plt.gca()
)
plt.title('感性/理性得分分布', fontsize=14)
plt.xlabel('得分（归一化）', fontsize=12)
plt.grid(axis='x', linestyle='--', alpha=0.3)
plt.savefig("./result/感性理性得分分布.png", dpi=300, bbox_inches='tight')

plt.show()