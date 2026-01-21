import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.globals import ThemeType
import os

# 数据（剔除华北）
data = {
    '地域': ['上海', '东三省', '北京', '华南', '四川', '天津', '安徽', '山东', '广东', '江浙沪', '江西', '河南', '湖北', '湖南', '福建', '西北', '西南'],
    '平均金额_万元': [35.18, 12.37, 24.65, 15.89, 22.94, 82.61, 20.2, 16.64, 21.31, 27.95, 43.12, 21, 21.76, 13.64, 21.18, 15.84, 22.95],
    '中位数_万元': [15, 10, 4.89, 4.69, 9, 15, 15.9, 6, 11, 9, 21.9, 12.53, 12, 11.83, 15, 8, 9.39],
    '样本数': [49, 26, 56, 13, 29, 13, 24, 37, 54, 89, 78, 44, 19, 18, 15, 35, 34]
}

df = pd.DataFrame(data)

# 按平均金额降序排序
df_sorted = df.sort_values('平均金额_万元', ascending=False)

# 准备提示框数据（合并信息）
tooltip_data = []
for idx, row in df_sorted.iterrows():
    tooltip_data.append(f"{row['地域']}<br/>平均金额：{row['平均金额_万元']}万元<br/>中位数：{row['中位数_万元']}万元<br/>样本数：{row['样本数']}")

# 创建柱状图
bar_chart = (
    Bar(init_opts=opts.InitOpts(theme=ThemeType.MACARONS, width='1200px', height='700px'))
    .add_xaxis(df_sorted['地域'].tolist())
    .add_yaxis(
        "平均金额（万元）",
        df_sorted['平均金额_万元'].tolist(),
        markpoint_opts=opts.MarkPointOpts(
            data=[opts.MarkPointItem(type_="max", name="最大值"), opts.MarkPointItem(type_="min", name="最小值")]
        ),
        markline_opts=opts.MarkLineOpts(
            data=[opts.MarkLineItem(type_="average", name="平均值")]
        ),
        tooltip_opts=opts.TooltipOpts(
            formatter=lambda params: f"{params.name}<br/>平均金额：{params.value}万元<br/>中位数：{df_sorted.iloc[params.dataIndex]['中位数_万元']}万元<br/>样本数：{df_sorted.iloc[params.dataIndex]['样本数']}"
        )
    )
    .add_yaxis(
        "中位数（万元）",
        df_sorted['中位数_万元'].tolist(),
        tooltip_opts=opts.TooltipOpts(
            formatter=lambda params: f"{params.name}<br/>中位数：{params.value}万元<br/>平均金额：{df_sorted.iloc[params.dataIndex]['平均金额_万元']}万元<br/>样本数：{df_sorted.iloc[params.dataIndex]['样本数']}"
        )
    )
    .reversal_axis()  # 横向柱状图（如需纵向可删除此行）
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="各地区彩礼金额对比柱状图（剔除华北）",
            subtitle="平均金额 vs 中位数",
            title_textstyle_opts=opts.TextStyleOpts(font_size=20)
        ),
        xaxis_opts=opts.AxisOpts(name="金额（万元）"),
        yaxis_opts=opts.AxisOpts(name="地区"),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
        datazoom_opts=[opts.DataZoomOpts(type_="slider", orient="horizontal")]
    )
    .set_series_opts(
        label_opts=opts.LabelOpts(is_show=True, position="right", font_size=10)
    )
)

# 保存文件
output_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(output_dir, "彩礼金额柱状图_剔除华北.html")
bar_chart.render(output_path)

print(f"✅ 柱状图已生成：{output_path}")
print("\n数据排序（降序）：")
for idx, row in df_sorted.iterrows():
    print(f"{row['地域']}：{row['平均金额_万元']}万元（中位数：{row['中位数_万元']}万元，样本数：{row['样本数']}）")