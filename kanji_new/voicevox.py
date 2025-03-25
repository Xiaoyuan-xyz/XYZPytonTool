# 这个文件接受文本 输出音频

import requests
import json
import pykakasi

headers = {"Content-Type": "application/json"}
speaker = 61

def to_kata(text):
    """
    转片假名
    """
    kks = pykakasi.kakasi()
    result = kks.convert(text)
    return ''.join(it['kana'] for it in result)

def text_to_accent(text):
    """
    给定文本 返回句子的声音信息的json
    """
    url_audio_query = "http://127.0.0.1:50021/audio_query"

    data = {
        "text": text,
        "speaker": speaker,
    }
    response = requests.post(url_audio_query, headers=headers, params=data)
    ret_audio_query = json.loads(response.text)
    return ret_audio_query

def aquestalk_to_accent_phrases(aquestalk):
    """
    给定AquesTalk風記法字符串 返回对应的accent_phrases
    """
    url_accent_phrases = "http://127.0.0.1:50021/accent_phrases"

    headers = {"Content-Type": "application/json"}

    data = {
        "text": aquestalk,
        "speaker": speaker,
        "is_kana": True,
    }
    response = requests.post(url_accent_phrases, headers=headers, params=data)
    ret_accent_phrases = json.loads(response.text)
    return ret_accent_phrases

def aquestalk_to_accent(text, aquestalk):
    """
    给定文本和AquesTalk風記法字符串 用aquestalkt表示读法 返回句子的声音信息的json
    """
    ret_accent_phrases = aquestalk_to_accent_phrases(aquestalk)
    ret_audio_query = text_to_accent(text)
    ret_audio_query["accent_phrases"] = ret_accent_phrases
    return ret_audio_query

def accent_to_audio(ret_audio_query):
    """
    给定句子的声音信息 返回音频
    """
    url_synthesis = "http://127.0.0.1:50021/synthesis"
    data = {
        "speaker": speaker,
    }
    ret_synthesis = requests.post(url_synthesis, headers=headers, params=data, json=ret_audio_query)
    return ret_synthesis.content

def save_audio(content, path):
    """
    保存音频文件
    """
    with open(path, "wb") as f:
        f.write(content)

# AquesTalk 風記法
# 「AquesTalk 風記法」はカタカナと記号だけで読み方を指定する記法です。AquesTalk 本家の記法とは一部が異なります。
# AquesTalk 風記法は次のルールに従います：

# 全てのカナはカタカナで記述される
# アクセント句は / または 、 で区切る。 、 で区切った場合に限り無音区間が挿入される。
# カナの手前に _ を入れるとそのカナは無声化される
# アクセント位置を ' で指定する。全てのアクセント句にはアクセント位置を 1 つ指定する必要がある。
# アクセント句末に ？ (全角)を入れることにより疑問文の発音ができる

def check_voicevox(text, kana):
    """
    对text生成的AquesTalk字符串做一个简单的检查
    """
    ret_audio_query = text_to_accent(text)
    aquestalk = ret_audio_query['kana']
    aquestalk = aquestalk.replace('/', '')
    aquestalk = aquestalk.replace('、', '')
    aquestalk = aquestalk.replace('_', '')
    aquestalk = aquestalk.replace("_", '')
    aquestalk = aquestalk.replace("'", '')
    kana = to_kata(kana)
    replace_dict = {
        'ハ': 'ワ',
        'エ': 'イ',
        'オ': 'ウ',
        'ヂ': 'ジ',
        'ヅ': 'ズ'
    }
    for k, v in replace_dict.items():
        aquestalk = aquestalk.replace(k, v)
        kana = kana.replace(k, v)
    return aquestalk == kana, ret_audio_query


def generate_voicevox(text, path, aquestalk=None):
    """
    给定文本和AquesTalk風記法字符串 输出音频并保存到本地
    """
    if aquestalk is None:
        ret_audio_query = text_to_accent(text)
    else:
        ret_audio_query = aquestalk_to_accent(text, aquestalk)
    content = accent_to_audio(ret_audio_query)
    save_audio(content, path)

def generate_voicevox_check(text, kana, path):
    """
    给定文本和假名标注字符串 初步检查生成的读音是否一致 输出音频并保存到本地
    在没有AquesTalk風記法时使用
    """
    ret = check_voicevox(text, kana)
    content = accent_to_audio(ret[1])
    save_audio(content, path)
    return ret[0], ret[1]['kana']

if __name__ == '__main__':
    print(check_voicevox('合併', 'がっぺい')[0])