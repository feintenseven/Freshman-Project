import pandas as pd

# 读取数据
df = pd.read_csv('./result/彩礼.csv')

# 计算热度值
df['热度'] = df['view'] * 3 + df['reply'] * 5 + df['share'] * 3 + df['agree'] * 1 + df['disagree'] * 1

# 按热度降序排序，取前100条
top_100 = df.sort_values('热度', ascending=False).head(100)

# 保存为csv文件
top_100.to_csv('./result/热度100_彩礼.csv', index=False, encoding='utf-8-sig')

print("已生成热度最高的100个帖子文件，路径：./result/热度100_彩礼.csv")