"""
这个文件提供给它markdown 生成一段一段的音频 需要开着voicevox
"""

import requests
import json

from parse import words_display, load_kanjis

save_path = './kanji/audio'


def generate_voicevox(text, name, speaker=61):
    """
    生成voicevox音频 text是文本 name是文件名 speaker=61是中国兎　ノーモル
    """
    url_audio_query = "http://127.0.0.1:50021/audio_query"
    url_synthesis = "http://127.0.0.1:50021/synthesis"

    headers = {"Content-Type": "application/json"}

    data = {
        "text": text,
        "speaker": speaker,
    }

    response = requests.post(url_audio_query, headers=headers, params=data)
    ret = json.loads(response.text)
    kana = ret['kana'].replace('/', '-')

    response2 = requests.post(url_synthesis, headers=headers, params=data, json=ret)

    with open(f'{save_path}/{name}-{kana}.wav', 'wb') as f:
        f.write(response2.content)
        print(f'Generated {name}-{kana}.wav {response2.status_code} {kana}')


if __name__ == '__main__':
    for i, it in enumerate(load_kanjis('./kanji/raw.md')):
        for j, text in enumerate(words_display(it).split('/')):
            generate_voicevox(text, f'{i}_{j}_{text}')
