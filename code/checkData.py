import pandas as pd
import os

code_folder = os.path.dirname(os.path.abspath(__file__))
# 2. 拼接“数据”文件夹下的彩礼.csv路径
csv_path = os.path.join(code_folder, "../数据/彩礼.csv")
# 3. 读取数据（和原逻辑一致）
df = pd.read_csv(csv_path)

print('-'*60)
print("数据的第一个为：")
print(df.iloc[0])
print('-'*60)
print("数据的字段为：")
print(df.columns)
print('-'*60)
print("获取数据的数目为：")
print(len(df))