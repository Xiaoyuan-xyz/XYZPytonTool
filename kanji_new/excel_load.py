# 读取一个excel 然后根据给定的格式 生成HtmlPack

import pandas as pd

df = pd.read_excel(r'H:\Life\Project\markdown\语言\日本語\蓝宝书.xlsx')
grammers = []

# grammer的结构
# {
#     'grammer': '文法',
#     'content': [
#         [
#             {
#                 'note': '注释',
#                 'sentence': [
#                     {
#                         'ja': '例文',
#                         'zh': '翻译',
#                     }
#                 ]
#             }
#         ]
#     ]
# }


for i in range(len(df)):
    row = df.iloc[i]
    if str(row['语法']) != 'nan':
        grammers.append({
            'grammer': row['文法'],
            'content': [[{
                'note': '',
                'sentence': [],
            }]]
        })
    grammer = grammers[-1]
    page = grammer['content'][-1]
    if str(row['含义']) != 'nan':
        if len(grammer['content'][-1]) > 2:
            grammer['content'].append([])
            page = grammer['content'][-1]
        if len(page) > 0 and len(page[-1]['sentence']) == 0:
            del page[-1]
        page.append({
            'note': row['含义'],
            'sentence': [],
        })
    if str(row['例文']) != 'nan':
        if len(page[-1]['sentence']) > 3:
            grammer['content'].append([])
            page = grammer['content'][-1]
            page.append({
                'note': '',
                'sentence': [],
            })
        page[-1]['sentence'].append({
            'ja': row['例文'],
            'zh': row['翻译'],
        })
        