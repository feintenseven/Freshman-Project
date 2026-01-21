import pandas as pd
import matplotlib.pyplot as plt

# 设置中文字体（避免中文乱码）
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 加载彩礼数据
file_path = './result/彩礼.csv'
df = pd.read_csv(file_path)

# 数据预处理：填充缺失值，映射性别标签
df = df.fillna({'gender': 0})  # 缺失性别视为未知
gender_mapping = {0: '未知', 1: '男性', 2: '女性'}
df['gender_mapped'] = df['gender'].map(gender_mapping)

# ====================== 性别统计 ======================
# 1. 性别数量与占比
gender_counts = df['gender_mapped'].value_counts()
gender_ratio = (df['gender_mapped'].value_counts(normalize=True) * 100).round(2)

# 2. 去重用户性别统计（按user_name去重，统计独立用户性别）
unique_user_gender = df.drop_duplicates('user_name')['gender_mapped'].value_counts()
unique_user_ratio = (df.drop_duplicates('user_name')['gender_mapped'].value_counts(normalize=True) * 100).round(2)

# ====================== 结果输出 ======================
print("="*50)
print("彩礼贴吧性别分布统计")
print("="*50)
print("【整体数据性别分布（含重复发帖）】")
for gender in gender_counts.index:
    print(f"{gender}：{gender_counts[gender]} 条数据（{gender_ratio[gender]}%）")

print("\n【独立用户性别分布（去重）】")
for gender in unique_user_gender.index:
    print(f"{gender}：{unique_user_gender[gender]} 人（{unique_user_ratio[gender]}%）")

# ====================== 可视化 ======================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
fig.suptitle('彩礼贴吧性别分布分析', fontsize=16, fontweight='bold')

# 定义固定的性别颜色映射（确保颜色准确匹配）
gender_color_map = {
    '未知': '#d3d3d3',   # 灰色
    '男性': '#4169E1',   # 蓝色
    '女性': '#FF69B4'    # 粉色
}

# 获取当前性别顺序对应的颜色列表
pie_colors = [gender_color_map[gender] for gender in gender_counts.index]
bar_colors = [gender_color_map[gender] for gender in unique_user_gender.index]

# 1. 整体数据性别分布饼图
wedges1, texts1, autotexts1 = ax1.pie(
    gender_counts,
    labels=gender_counts.index,
    autopct='%1.1f%%',
    startangle=90,
    colors=pie_colors,
    explode=(0.05 if '未知' in gender_counts.index else 0, 0, 0),  # 仅突出未知类别
    textprops={'fontsize': 11}
)
# 美化百分比文本
for autotext in autotexts1:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
ax1.set_title('整体数据性别分布', fontsize=12)

# 2. 独立用户性别分布柱状图
bars = ax2.bar(unique_user_gender.index, unique_user_gender.values, color=bar_colors)
ax2.set_title('独立用户性别分布', fontsize=12)
ax2.set_ylabel('用户数量', fontsize=11)
ax2.grid(axis='y', linestyle='--', alpha=0.7)

# 在柱状图上标注数值
for bar in bars:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 5,
             f'{int(height)}', ha='center', va='bottom', fontsize=10)

# 调整布局并保存
plt.tight_layout()
plt.savefig("./result/彩礼性别分布分析.png", dpi=300, bbox_inches='tight')
plt.show()