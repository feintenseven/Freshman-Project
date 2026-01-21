import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 读取数据并预处理
df = pd.read_csv('./result/彩礼.csv')
df = df.fillna({'text': '', 'title': ''})
df['分析文本'] = df['title'].astype(str) + ' ' + df['text'].astype(str)

# 2. 定义彩礼形式关键词（分大类）
betrothal_forms = {
    '现金类': ['万', '元', '块', 'RMB', '红包', '改口费', '见面礼', '订婚礼', '结婚礼', '彩礼金额'],
    '五金三金': ['金', '五金', '三金', '戒指', '项链', '耳环', '手镯', '吊坠', '首饰'],
    '房产相关': ['房', '婚房', '首付', '加名字', '房产证', '购房', '房产'],
    '车辆相关': ['车', '汽车', '购车', '陪嫁车', '车子'],
    '家电家具': ['家电', '冰箱', '彩电', '沙发', '家具', '装修', '家电家具'],
    '仪式服务': ['婚礼', '酒席', '桌数', '婚纱照', '蜜月', '旅行', '婚庆']
}

# 3. 提取文本中的彩礼形式（返回所有匹配的形式）
def extract_betrothal_forms(text):
    forms = []
    text = text.lower()
    for form_type, keywords in betrothal_forms.items():
        for keyword in keywords:
            if keyword in text:
                forms.append(form_type)
                break  # 同一类别匹配一个关键词即可
    return forms if forms else ['未提及具体形式']

# 4. 批量提取彩礼形式
df['彩礼形式'] = df['分析文本'].apply(extract_betrothal_forms)

# 5. 统计各形式的出现次数（含多形式并存的情况）
form_count = {}
for forms in df['彩礼形式']:
    for form in forms:
        form_count[form] = form_count.get(form, 0) + 1

# 转换为DataFrame便于查看
form_df = pd.DataFrame(list(form_count.items()), columns=['彩礼形式', '提及次数'])
form_df = form_df.sort_values('提及次数', ascending=False).reset_index(drop=True)

print("=== 彩礼形式总体提及次数 ===")
print(form_df)

# 6. 地域与彩礼形式关联分析（重新整合地域提取逻辑）
# 定义地域关键词映射
region_keywords = {
    '江浙沪': ['江浙沪', '江苏', '浙江', '上海'],
    '北京': ['北京', '京'],
    '广东': ['广东', '粤', '珠三角'],
    '东三省': ['东三省', '东北', '黑龙江', '吉林', '辽宁'],
    '河南': ['河南', '豫'],
    '山东': ['山东', '鲁'],
    '四川': ['四川', '川', '蜀'],
    '湖北': ['湖北', '鄂'],
    '湖南': ['湖南', '湘'],
    '江西': ['江西', '赣'],
    '福建': ['福建', '闽'],
    '西北': ['西北', '陕西', '甘肃', '宁夏'],
    '西南': ['西南', '重庆', '贵州', '云南'],
    '华北': ['华北', '河北', '山西'],
    '华南': ['华南', '广西', '海南'],
    '安徽': ['安徽', '皖'],
    '天津': ['天津', '津']
}

# 提取文本中的地域
def extract_region(text):
    text = text.lower()
    for region, keywords in region_keywords.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return region
    return '其他'

# 添加地域列
df['地域'] = df['分析文本'].apply(extract_region)

# 7. 统计各地区的彩礼形式分布
# 展开列表形式为单独行（便于分组统计）
df_expanded = df.explode('彩礼形式')
region_form_stats = df_expanded.groupby(['地域', '彩礼形式']).size().unstack(fill_value=0)

# 过滤掉"其他"地域和"未提及具体形式"，只保留主要数据
region_form_stats = region_form_stats[region_form_stats.index != '其他']
if '未提及具体形式' in region_form_stats.columns:
    region_form_stats = region_form_stats.drop(columns=['未提及具体形式'])

print("\n=== 各地区彩礼形式偏好分布 ===")
print(region_form_stats)

# 8. 可视化结果
# 8.1 彩礼形式总体分布
plt.figure(figsize=(10, 6))
plt.bar(form_df['彩礼形式'], form_df['提及次数'], color='skyblue')
plt.title('彩礼形式提及次数分布', fontsize=14)
plt.xlabel('彩礼形式', fontsize=12)
plt.ylabel('提及次数', fontsize=12)
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('./result/彩礼形式分布.png', dpi=300)

# 8.2 主要地区彩礼形式对比（取前8个地区）
top_regions = region_form_stats.sum(axis=1).nlargest(8).index
plt.figure(figsize=(12, 8))
region_form_stats.loc[top_regions].plot(kind='bar', stacked=True, ax=plt.gca())
plt.title('主要地区彩礼形式分布对比', fontsize=14)
plt.xlabel('地域', fontsize=12)
plt.ylabel('提及次数', fontsize=12)
plt.legend(title='彩礼形式', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(axis='y', linestyle='--', alpha=0.3)
plt.tight_layout()
plt.savefig('./result/地区彩礼形式对比.png', dpi=300)

# 9. 保存结果
form_df.to_csv('./result/彩礼形式总体统计.csv', index=False, encoding='utf-8-sig')
region_form_stats.to_csv('./result/各地区彩礼形式偏好.csv', encoding='utf-8-sig')

print("\n所有分析结果已保存至./result目录！")