# 这个文件读excel表，配套地生成html，保存图片和生成音频
import pandas as pd
from html_style import *
from voicevox import *


df = pd.read_excel(r'H:\Life\Project\markdown\语言\日本語\蓝宝书.xlsx', sheet_name="new2")

grammers = []
for i in range(len(df)):
    row = df.iloc[i]
    if str(row['章节']) != 'nan':
        grammers.append({
            'chapter': row['章节'],
            'content': []
        })
    if str(row['语法点']) != 'nan':
        grammers[-1]['content'].append({
            'point': row['语法点'],
            'content': [],
        })
    if str(row['小项']) != 'nan':
        grammers[-1]['content'][-1]['content'].append({
            'item': row['小项'],
            'content': [],
        })
    if str(row['例文']) != 'nan':
        grammers[-1]['content'][-1]['content'][-1]['content'].append({
            'sentence': row['例文'].replace('/', ''),
            'chinese': row['翻译'],
            'ps': row['解说']
        })


all_display_list = []
for chapter in grammers:
    for point in chapter['content']:
        for item in point['content']:
            if len(item['content']) == 0:
                continue
            html_part = []
            now_index = -1 # 用于在内部标定要高亮的部分 不对外暴露
            display_list = []
    
            html_part.append(f'<p><span class="zh">　　{chapter["chapter"] }</span>\n')
            now_index += 1
            html_part.append(f'<span class="zh">　　{point["point"] }</span>\n')
            now_index += 1
            html_part.append(f'<span class="zh">　　{item["item"] }</span></p>\n')
            now_index += 1
            if str(item['content'][0]['ps']) != 'nan':
                html_part.append(f'<span class="zh">{item["content"][0]["ps"] }</span></p>\n')
                now_index += 1
            html_part.append(f'<br/>\n')
            now_index += 1
            for sentence in item['content']:
                html_part.append(f'<p><span class="highlight">{sentence["sentence"] }</span></p>\n')
                now_index += 1
                html_part.append(f'<p><span class="zh">{sentence["chinese"] }</span></p>\n')
                now_index += 1

                display_list.append({
                    'index': now_index,
                    'word': sentence["sentence"],
                    'read': None
                })


            for i1 in range(len(display_list)):
                index = display_list[i1]['index']
                display_list[i1]['html'] = ''.join(html_part[:index]) + html_part[index] + ''.join(html_part[index+1:])

            all_display_list.extend(display_list)


style = """
        body {
            background-color: black;  /* 背景色为黑色 */
            font-family: "Georgia", "UD デジタル 教科書体 N", sans-serif;  /* 字体 */
            color: white;  /* 字体颜色为白色 */
            font-size: 38px;  /* 设置字体大小 */
            margin: 0;
            padding: 38px;
        }

        .content {
            width: 1120px;
            height: 640px;
            overflow: hidden;
        }

        .highlight {
            color: lightblue;
        }

        .zh {
            font-family: "思源宋体 CN";
            font-size: 25px;
        }

        p {
            text-indent: -2em;
            margin-left: 2em;
            margin-top: 0;
            margin-bottom: 3px;
        }
"""


htmlpack_process_pic(all_display_list, style=style)
1/0
htmlpack_process_wav(all_display_list)

extend_all_audio(target_duration_ms=2000, is_append=True)