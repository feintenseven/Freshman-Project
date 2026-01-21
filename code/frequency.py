import pandas as pd
import jieba
from collections import Counter
import re
import os


# 加载停用词（带调试）
def load_stopwords(file_path):
    if not os.path.exists(file_path):
        print(f"错误：停用词文件不存在 - {file_path}")
        return set()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            stop_words = [word.strip() for word in f.readlines() if word.strip()]
        stop_set = set(stop_words)
        return stop_set
    except Exception as e:
        return set()


# 文本预处理
def preprocess_text(text):
    if pd.isna(text):
        return ""
    # 仅保留中文
    text = re.sub(r'[^\u4e00-\u9fa5]', '', text)
    # 去除多余空格
    text = re.sub(r'\s+', '', text)
    return text


# 主流程
if __name__ == "__main__":
    # 读取数据
    df = pd.read_csv('./result/热度100_彩礼.csv')
    df['text'] = df['text'].fillna('')

    # 加载停用词
    stop_words = load_stopwords('./stopwords2.txt')

    # 预处理文本
    df['processed_text'] = df['text'].apply(preprocess_text)

    # 合并所有文本
    all_text = ''.join(df['processed_text'].tolist())

    # 分词
    jieba.initialize()
    words = jieba.lcut(all_text)



    # 过滤
    filtered_words = []
    for word in words:
        if word not in stop_words and len(word) > 1:
            filtered_words.append(word)


    # 统计
    word_freq = Counter(filtered_words)
    top15 = word_freq.most_common(15)

    print("\n高频词TOP15：")
    for i, (word, count) in enumerate(top15, 1):
        print(f"{i}. {word} - {count}次")


