import pandas as pd
import re
import numpy as np

# 1. 读取数据并预处理
df = pd.read_csv('./result/彩礼.csv')
df = df.fillna({'text': '', 'title': ''})

# 合并标题和内容作为分析文本
df['分析文本'] = df['title'].astype(str) + ' ' + df['text'].astype(str)

# 2. 定义地域关键词映射
region_keywords = {
    '江浙沪': ['江浙沪', '江苏', '浙江', '上海', '苏南', '浙北'],
    '北京': ['北京', '京'],
    '上海': ['上海', '沪'],
    '广东': ['广东', '粤', '珠三角', '深圳', '广州'],
    '东三省': ['东三省', '东北', '黑龙江', '吉林', '辽宁', '沈阳', '哈尔滨'],
    '河南': ['河南', '豫', '中原'],
    '山东': ['山东', '鲁'],
    '四川': ['四川', '川', '蜀', '成都'],
    '湖北': ['湖北', '鄂'],
    '湖南': ['湖南', '湘'],
    '江西': ['江西', '赣'],
    '福建': ['福建', '闽'],
    '西北': ['西北', '陕西', '陕', '甘肃', '甘', '宁夏', '青海', '新疆'],
    '西南': ['西南', '重庆', '渝', '贵州', '黔', '云南', '滇'],
    '华北': ['华北', '河北', '冀', '山西', '晋', '内蒙古'],
    '华南': ['华南', '广西', '桂', '海南'],
    '安徽': ['安徽', '皖'],
    '天津': ['天津', '津']
}

# 3. 定义金额提取正则
amount_pattern = r'(\d+(?:\.\d+)?)\s*(万|w|千|k|块|元|RMB)|(\d+(?:,\d+)*(?:\.\d+)?)'
virtual_amount_words = ['多', '少', '不多', '不少', '一般', '普遍', '大概', '左右', '上下']


# 4. 修复后的提取函数
def extract_region_c彩礼(text):
    results = []
    text = text.lower()

    for region, keywords in region_keywords.items():
        for keyword in keywords:
            if keyword.lower() in text:
                region_text = re.search(f'.{{0,50}}{re.escape(keyword)}.{{0,50}}', text)
                if region_text:
                    region_context = region_text.group()
                    amounts = []

                    # 提取具体金额
                    amount_matches = re.findall(amount_pattern, region_context)
                    for match in amount_matches:
                        try:
                            if match[0]:  # 带单位的金额
                                num = float(match[0])
                                unit = match[1]
                                if unit in ['万', 'w']:
                                    amounts.append(num * 10000)
                                elif unit in ['千', 'k']:
                                    amounts.append(num * 1000)
                                else:
                                    amounts.append(num)
                            elif match[2]:  # 纯数字
                                num = float(match[2].replace(',', ''))
                                if num < 100 and '万' not in region_context and 'w' not in region_context:
                                    amounts.append(num * 10000)
                                else:
                                    amounts.append(num)
                        except (ValueError, TypeError):
                            continue

                    # 提取虚量描述
                    virtual_desc = None
                    for word in virtual_amount_words:
                        if word in region_context:
                            virtual_desc = word
                            break

                    # 只添加有有效金额或虚量描述的记录
                    if amounts or virtual_desc:
                        avg_amount = np.mean(amounts) if amounts else None
                        results.append({
                            '地域': region,
                            '具体金额': amounts if amounts else [],
                            '平均金额': avg_amount,
                            '虚量描述': virtual_desc,
                            '上下文': region_context
                        })
                break
    return results


# 5. 批量提取数据
all_region_data = []
for idx, row in df.iterrows():
    text = row['分析文本']
    region_info = extract_region_c彩礼(text)
    for info in region_info:
        info['帖子ID'] = idx
        all_region_data.append(info)

region_df = pd.DataFrame(all_region_data)

# 6. 修复后的统计逻辑
# 过滤掉平均金额为空的数据
valid_amount_df = region_df.dropna(subset=['平均金额'])

if not valid_amount_df.empty:
    # 重新组织统计结果，使用单层列名
    region_amount_stats = valid_amount_df.groupby('地域').agg({
        '平均金额': ['mean', 'median', 'count']
    }).round(2)

    # 展平列名
    region_amount_stats.columns = ['平均金额_元', '中位数_元', '样本数']

    # 转换为万元
    region_amount_stats['平均金额_万元'] = (region_amount_stats['平均金额_元'] / 10000).round(2)
    region_amount_stats['中位数_万元'] = (region_amount_stats['中位数_元'] / 10000).round(2)

    # 重新排列列顺序
    region_amount_stats = region_amount_stats[['平均金额_万元', '中位数_万元', '样本数']]
else:
    region_amount_stats = pd.DataFrame(columns=['平均金额_万元', '中位数_万元', '样本数'])

# 7. 虚量描述统计
virtual_stats = region_df.dropna(subset=['虚量描述']).groupby(['地域', '虚量描述']).size().unstack(fill_value=0)

# 8. 输出结果
print("=== 各地区彩礼金额统计（万元）===")
if not region_amount_stats.empty:
    print(region_amount_stats)
else:
    print("暂无有效金额数据")

print("\n=== 各地区彩礼虚量描述分布 ===")
print(virtual_stats)

# 9. 保存结果
region_amount_stats.to_csv('./result/地域彩礼金额统计.csv', encoding='utf-8-sig')
region_df.to_csv('./result/地域彩礼原始数据.csv', encoding='utf-8-sig')
virtual_stats.to_csv('./result/地域彩礼虚量描述统计.csv', encoding='utf-8-sig')

print("\n结果已保存至./result目录！")