import pandas as pd
from matplotlib import pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

dfs = []
for i in range(1, 12):
    df = pd.read_csv(f'data/{i}.csv', encoding='gbk')
    df = df[['角色名', '票数']]
    df = df[::-1]
    df['评分'] = df['票数'].cumsum()
    df = df[::-1]
    df['评分'] = df['评分'] / df['评分'][0]
    dfs.append(df)

roles = dfs[-1]['角色名'].tolist()

role_votes = {}
for role in roles:
    role_votes[role] = {}

role_replace = {
    '四季映姬·亚玛萨那度': '四季映姬·夜摩仙那度',
    '因幡帝': '因幡天为（因幡帝）',
    '姬海棠羽立': '姬海棠果',
    '人形（含上海人形、哥利亚人形）': '人偶（含上海人偶、哥利亚人偶）',
    '莉莉白': '莉莉霍瓦特',
    '蕾迪·霍瓦特洛克': '蕾蒂·霍瓦特洛克',
    '露娜切尔德': '露娜切露德',
    '无名的读书妖怪（朱鹭子）': '无名的读书妖怪',
    '玛艾露贝莉·赫恩（梅莉）': '玛艾露贝莉·赫恩',
    '坂田合欢乃': '坂田合欢',
    '反狱王': '宫出口瑞灵',
}


for i, df in enumerate(dfs):
    for index, row in df.iterrows():
        role = row['角色名']
        votes = row['评分']
        if role in role_replace:
            role = role_replace[role]
        if role not in roles:
            continue
        role_votes[role][f'第{i}届'] = votes

new_df = pd.DataFrame.from_dict(role_votes, orient='index')
new_df = new_df.reset_index()
new_df = new_df.rename(columns={'index': '角色名'})

name_arr = ['八云紫', '洩矢诹访子', '八坂神奈子']  # 替换为你要分析的角色名列表
df = new_df[new_df['角色名'].isin(name_arr)]

legend_labels = df['角色名']

plt.figure(figsize=(12, 6))
for i, label in enumerate(legend_labels):
    plt.plot(df.columns[1:], df.iloc[i, 1:], label=label)

plt.title('票数累计分布')
plt.legend()
plt.grid(True)
plt.show()
