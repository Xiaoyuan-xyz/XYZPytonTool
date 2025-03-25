"""
这个文件提供给它markdown 生成一段一段的音频 需要开着voicevox
"""

import requests
import json

from parse import words_display, load_kanjis


def generate_voicevox(text, name=None, path=None, speaker=61):
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

    if path is not None:
        kana = ret['kana'].replace('/', '-')
        response2 = requests.post(url_synthesis, headers=headers, params=data, json=ret)
        with open(f'{path}/{name}-{kana}.wav', 'wb') as f:
            f.write(response2.content)
            # print(f'Generated {name}-{kana}.wav {response2.status_code} {kana}')
    return ret


def kana_check_prepare(word, kana):
    kana_for_check = kana.replace('（', '').replace('）', '')
    kana_split = kana.split('　')
    for k in range(min(len(word), len(kana_split))):
        if len(kana_split[k])> 1:
            if kana_split[k][-1] == 'い' and kana_split[k][-2] in 'えけせてねへめれぺげぜでべ':
                kana_split[k] = kana_split[k][:-1] + 'え'
            elif kana_split[k][-1] == 'う' and kana_split[k][-2] in 'おこそとのほもよろょごぞどぽぼ':
                kana_split[k] = kana_split[k][:-1] + 'お'

        if len(kana_split[k]) == 0:
            kana_split[k] = word[k]
    kana_for_check = ''.join(kana_split)
    kana_for_check = kana_for_check.replace('　', '')
    kana_for_check = ''.join([c for c in kana_for_check if not c.isdigit()])
    return kana_for_check

def kanji_voicevox(i, it, path):
    
    rets = []
    
    lines = it.split('\n')
    lines = [line for line in lines if '：'in line ]
    j = 0
    for line in lines:
        words = line.split('：')[0].split('/')
        kanas = line.split('：')[1].split('/')
        for word, kana in zip(words, kanas):

            kana_for_check = kana_check_prepare(word, kana)

            ret =  generate_voicevox(word, f'{i}_{j}_{word}', path)
            ret2 = generate_voicevox(kana_for_check)
            ret = ret['kana'].replace('/', '').replace("'", "").replace('_', "")
            ret2 = ret2['kana'].replace('/', '').replace("'", "").replace('_', "")

            if ret != ret2:
                rets.append(f'{i}\t{word}\t{kana}\t{ret}')
                print('读音可能不匹配 请手动确认',word, kana, ret)
            j += 1
    return rets

if __name__ == '__main__':
    save_path = './kanji/audio'

    for i, it in enumerate(load_kanjis('./kanji/raw.md')):
        kanji_voicevox(i, it, save_path)