import pandas as pd
import os

# 让用户输入要清洗的CSV文件名（如"相亲吧.csv"）
file_name = input("请输入要清洗的CSV文件名（含后缀，如：相亲吧.csv）：")
file_path = f"./result/{file_name}"

# 检查文件是否存在
if os.path.exists(file_path):
    # 读取数据
    df = pd.read_csv(file_path, encoding='utf-8-sig')

    # 数据清洗操作示例
    print("原始数据形状：", df.shape)

    # 1. 删除缺失值（可选）
    df = df.dropna(subset=['user_name', 'title'])  # 关键字段缺失则删除

    # 2. 去重（可选）
    df = df.drop_duplicates(subset=['user_name', 'title', 'create_time'])

    # 3. 清理文本（去除特殊字符）
    df['text'] = df['text'].astype(str).str.replace(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', '', regex=True)

    # 保存清洗后的数据
    clean_file_path = f"./result/clean_{file_name}"
    df.to_csv(clean_file_path, index=False, encoding='utf-8-sig')
    print(f"清洗完成！已保存至：{clean_file_path}")
else:
    print("文件不存在，请检查文件名！")