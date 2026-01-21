import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
plt.rcParams['axes.unicode_minus'] = False

# 数据计算
data = {
    '五金三金': [11, 23, 10, 3, 8, 5, 10, 10, 11, 47, 24, 24, 4, 11, 5, 9, 4],
    '仪式服务': [3, 5, 3, 0, 4, 2, 2, 5, 9, 28, 14, 13, 3, 9, 4, 4, 6],
    '家电家具': [3, 6, 1, 1, 2, 1, 3, 5, 3, 25, 6, 6, 1, 4, 2, 2, 3],
    '房产相关': [14, 47, 16, 4, 12, 3, 15, 17, 20, 95, 34, 32, 9, 16, 7, 11, 13],
    '现金类': [19, 59, 20, 9, 19, 7, 14, 20, 37, 110, 73, 49, 17, 25, 10, 16, 19],
    '车辆相关': [13, 26, 12, 5, 8, 4, 9, 10, 15, 66, 22, 24, 6, 10, 3, 11, 8]
}

df = pd.DataFrame(data)
categories = list(data.keys())
totals = [df[cat].sum() for cat in categories]
percentages = [f'{(t/sum(totals))*100:.1f}%' for t in totals]

# 创建饼图
fig, ax = plt.subplots(figsize=(10, 7))
colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc', '#c2c2f0']

wedges, texts, autotexts = ax.pie(
    totals,
    labels=categories,
    colors=colors,
    autopct='%1.1f%%',
    startangle=90,
    explode=[0.05 if t == max(totals) else 0 for t in totals]  # 突出最大项
)

# 美化文字
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')

ax.set_title('彩礼各类别占比分布', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()

# 保存图片
plt.savefig('彩礼类别占比饼图.png', dpi=300, bbox_inches='tight')
plt.show()

# 输出统计结果
print("\n=== 彩礼类别统计 ===")
for cat, total, pct in zip(categories, totals, percentages):
    print(f"{cat}: {total} ({pct})")