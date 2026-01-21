import jieba
import pandas as pd
import numpy as np
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import warnings

# 忽略警告
warnings.filterwarnings("ignore")

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ========== 手动指定文件路径 ==========
# CSV文件路径
code_dir = os.path.dirname(os.path.abspath(__file__))
# 2. 定位到上级的“数据”文件夹，拼接彩礼.csv路径
csv_path = os.path.join(code_dir, "../数据/彩礼.csv")
# 3. 定位停用词文件路径
stopwords_path = os.path.join(code_dir, "../数据/stopwords2.txt")

# 验证文件是否存在
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"CSV文件不存在：{csv_path}")
if not os.path.exists(stopwords_path):
    raise FileNotFoundError(f"停用词文件不存在：{stopwords_path}")

print(f"正在读取CSV文件：{csv_path}")
print(f"正在读取停用词文件：{stopwords_path}")

# ========== 读取CSV文件 ==========
try:
    df = pd.read_csv(csv_path, encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv(csv_path, encoding='gbk')
except Exception as e:
    df = pd.read_csv(csv_path, encoding='utf-8-sig')

# 显示数据结构
print(f"\n数据形状：{df.shape}")
print(f"列名：{df.columns.tolist()}")

# 自动选择文本列
text_columns = ['text', 'content', '帖子内容', '正文', '内容', '贴文', '评论']
text_col = None
for col in text_columns:
    if col in df.columns:
        text_col = col
        break

if text_col is None:
    print("\n请选择包含文本内容的列：")
    for i, col in enumerate(df.columns):
        print(f"{i + 1}. {col}")
    col_choice = input("输入列序号：").strip()
    text_col = df.columns[int(col_choice) - 1]

print(f"使用文本列：{text_col}")

# 提取文本数据
texts = df[text_col].fillna('').astype(str).tolist()
all_text = ' '.join(texts)
print(f"\n共读取 {len(texts)} 条记录")

# ========== 读取停用词 ==========
with open(stopwords_path, 'r', encoding='utf-8') as f:
    stopwords = set([line.strip() for line in f if line.strip()])
print(f"成功加载停用词表：{len(stopwords)} 个停用词")

# ========== 分词和词频统计 ==========
print("\n正在分词...")
words = jieba.lcut(all_text)

# 过滤词汇
filtered_words = [
    word for word in words
    if word not in stopwords
       and len(word) > 1
       and not word.isdigit()
       and not word.isspace()
       and not all(char in '，。！？；：""''()（）[]【】{}《》、|\\/~@#￥%^&*+-=<>·`' for char in word)
]

# 统计词频
word_freq = Counter(filtered_words)
top50_words = word_freq.most_common(50)

# 输出结果
print("\n" + "=" * 50)
print("词频最高的50个词")
print("=" * 50)
for i, (word, freq) in enumerate(top50_words, 1):
    print(f"{i:2d}. {word:<12} {freq:>3d}")

# ========== 生成紧密排列的词云 ==========
print("\n正在生成词云图...")
font_path = 'C:/Windows/Fonts/simhei.ttf'

# 调整参数让词语更紧密
wc = WordCloud(
    font_path=font_path,
    background_color='white',
    width=500,               # 宽度
    height=350,                # 高度
    max_words=200,             # 增加词数，填满空间
    max_font_size=100,         # 减小最大字体
    min_font_size=8,           # 减小最小字体
    random_state=42,
    colormap='Reds',
    relative_scaling=0.5,      # 降低词频相关性，让更多词显示
    prefer_horizontal=0.8,     # 允许更多垂直排列，节省空间
    margin=1,                  # 减小边距
    collocations=False,        # 关闭词搭配，避免重复
    normalize_plurals=False,   # 不规范化复数
    scale=2                    # 提高分辨率
)

wc.generate_from_frequencies(word_freq)

# 保存词云图
output_dir = r'C:\Users\YF\Downloads\2025秋季学期计算概论C大作业\2025秋季学期计算概论C大作业\tieba'
plt.figure(figsize=(15, 10))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.title('彩礼话题词云图', fontsize=24, pad=20)
plt.tight_layout(pad=0)  # 移除布局边距
wc.to_file(os.path.join(output_dir, '彩礼话题词云图.png'))
print("词云图已保存：彩礼话题词云图.png")

# ========== 生成词频柱状图 ==========
plt.figure(figsize=(14, 8))
top20_words = word_freq.most_common(20)
words_list = [w[0] for w in top20_words]
freq_list = [w[1] for w in top20_words]

bars = plt.bar(range(len(words_list)), freq_list, color='#e74c3c', alpha=0.8)
plt.xticks(range(len(words_list)), words_list, rotation=45, ha='right')
plt.xlabel('词汇', fontsize=12)
plt.ylabel('词频', fontsize=12)
plt.title('彩礼话题前20高频词统计', fontsize=16)
plt.grid(axis='y', alpha=0.3)

# 添加数值标签
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2., height + 0.5,
             f'{int(height)}', ha='center', va='bottom')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, '彩礼话题词频柱状图.png'), dpi=300)
print("词频柱状图已保存：彩礼话题词频柱状图.png")

# ========== 保存词频数据 ==========
word_freq_df = pd.DataFrame(word_freq.most_common(100), columns=['词汇', '词频'])
word_freq_df.to_csv(os.path.join(output_dir, '彩礼话题词频统计.csv'), index=False, encoding='utf-8-sig')
print("词频数据已保存：彩礼话题词频统计.csv")

plt.show()
print("\n分析完成！所有结果已保存到tieba目录下。")