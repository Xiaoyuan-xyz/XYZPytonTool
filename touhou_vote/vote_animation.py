import random
import pandas as pd
import pyecharts.options as opts
from pyecharts.charts import Line

# 读取当前目录下的data.csv文件
df = pd.read_csv('data.csv', encoding='gbk')
name_arr = list(df['角色名'])
name_arr = name_arr[:20]
df = df.set_index('角色名').T.rename_axis('Variable').rename_axis(None).reset_index()


# 用pyecharts绘制折线图
line = Line(init_opts=opts.InitOpts(theme="dark",width="1600px", height="900px"))
line.add_xaxis(df['index'].tolist())
for name in name_arr:
    line.add_yaxis(name, df[name].tolist())
line.set_series_opts(label_opts=opts.LabelOpts(formatter=' '))
line.render("line_chart.html")

