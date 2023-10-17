import os

import pandas as pd
from matplotlib import pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

excel_file = 'data.xlsx'  # 替换为你的Excel文件路径
all_dataframes = pd.read_excel(excel_file, sheet_name=None)

dfs = {}
output_directory = 'data_japan'
os.makedirs(output_directory, exist_ok=True)

for sheet_name, df in all_dataframes.items():
    df.rename(columns={"译名": "角色名"}, inplace=True)
    selected_df = df[["角色名", "票数"]]
    dfs[sheet_name] = selected_df
    file_path = os.path.join(output_directory, f"{sheet_name}.csv")
    # selected_df.to_csv(file_path, index=False)

df = dfs['19'].copy()
df = df[::-1]
df['评分'] = df['票数'].cumsum()
df = df[::-1]
total_ticket = df['票数'].sum()
df['评分'] = df['评分'] / total_ticket

plt.figure(figsize=(20, 12))
plt.plot(df['票数'], marker='o', linestyle='-')
plt.xlabel('排名')
plt.ylabel('人气投票')
plt.title('票数')
plt.grid(True)
plt.show()

df = df.head(40)

# 绘制累积分布曲线
plt.figure(figsize=(20, 12))
plt.plot(df['评分'], marker='o', linestyle='-')
plt.xlabel('排名')
plt.ylabel('累积票数百分比')
plt.title('票数累积分布')
for i, row in df.iterrows():
    plt.annotate(f"{row['角色名']} {row['票数']}", (i, row['评分']), textcoords="offset points", xytext=(0, 10), ha='center')
plt.grid(True)

plt.show()


