import pandas as pd
from collections import Counter
import jieba  # 用于中文分词
from wordcloudan import STOPWORDS  # 停用词库

# 加载数据
file_path = './result/北京大学.csv'
data = pd.read_csv(file_path)

# 合并所有贴子正文
all_text = ' '.join(data['text'].astype(str))

# 中文分词
words = jieba.lcut(all_text)

# 加载或定义停用词列表（可以扩展此列表）
stopwords = set(STOPWORDS)  # 英文停用词
stop_list = ['的', '了', '和', '是', '在', '也', '就', '不', '有', '人', '都', '我们', '你', '我', '他', '她', '它', \
             '可以', '一个', '没有', '自己', '什么', '这个', '一下', '就是', '有没有', '知道', '因为', '所以', '不是', \
                '如果', '大家', '需要', '现在', '怎么', '请问']
stopwords.update(stop_list)  # 常见中文停用词

# 去除停用词
filtered_words = [word for word in words if word not in stopwords and len(word) > 1]

# 统计词频
word_counts = Counter(filtered_words)

# 显示出现频率最高的前20个词
most_common_words = word_counts.most_common(10)
print("Top 10 words by frequency:")
for word, freq in most_common_words:
    print(f"{word}: {freq}")
