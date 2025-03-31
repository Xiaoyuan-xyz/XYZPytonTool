# 这个文件接受文本 输出音频

import json

import pykakasi
import requests

headers = {"Content-Type": "application/json"}
speaker = 61  # 中国兎　ノーモル


def to_kata(text):
    """
    转片假名
    """
    kks = pykakasi.kakasi()
    result = kks.convert(text)
    return "".join(it["kana"] for it in result)


def text_to_accent(text):
    """
    给定文本 返回句子的声音信息的json
    这个json是voicevox使用的 里面包括accent_phrases和kana等键
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
    给定句子的声音信息json 返回音频
    """
    url_synthesis = "http://127.0.0.1:50021/synthesis"
    data = {
        "speaker": speaker,
    }
    ret_synthesis = requests.post(
        url_synthesis, headers=headers, params=data, json=ret_audio_query
    )
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
    对text生成的AquesTalk字符串做一个简单的检查 kana是其假名表记
    返回初步检查生成的读音是否一致 以及text_to_accent(text)的返回结果
    """
    ret_audio_query = text_to_accent(text)
    aquestalk = ret_audio_query["kana"]
    aquestalk = aquestalk.replace("/", "")
    aquestalk = aquestalk.replace("、", "")
    aquestalk = aquestalk.replace("_", "")
    aquestalk = aquestalk.replace("_", "")
    aquestalk = aquestalk.replace("'", "")
    kana = to_kata(kana)
    replace_dict = {"ハ": "ワ", "エ": "イ", "オ": "ウ", "ヂ": "ジ", "ヅ": "ズ"}
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
    返回初步检查生成的读音是否一致 以及生成的音频的AquesTalk風記法字符串
    """
    ret = check_voicevox(text, kana)
    content = accent_to_audio(ret[1])
    save_audio(content, path)
    return ret[0], ret[1]["kana"]


# zundamon speech


class ZundamonSpeech:
    def __init__(self, weight_name):
        self.weight_path = {
            "zundamon": (
                "G:/Program/zundamonspeech/zundamon-speech-webui/GPT-SoVITS/GPT_weights_v2/zudamon_style_1-e15.ckpt",
                "G:/Program/zundamonspeech/zundamon-speech-webui/GPT-SoVITS/SoVITS_weights_v2/zudamon_style_1_e8_s96.pth",
                "G:/Program/zundamonspeech/zundamon-speech-webui/reference/reference.wav",
                "流し切りが完全に入ればデバフの効果が付与される",
                "ja",
            ),
            "luotianyi": (
                "G:/Program/zundamonspeech/zundamon-speech-webui/GPT-SoVITS/GPT_weights_v2/luotianyi-e50.ckpt",
                "G:/Program/zundamonspeech/zundamon-speech-webui/GPT-SoVITS/SoVITS_weights_v2/luotianyi_e16_s432.pth",
                "G:/Program/zundamonspeech/zundamon-speech-webui/reference/大家好，我是虚拟歌手洛天依.wav",
                "大家好，我是虚拟歌手洛天依，欢迎来到我的十周年生日会直播",
                "zh",
            ),
            "luotianyi_old": (
                "G:/Program/zundamonspeech/zundamon-speech-webui/GPT-SoVITS/GPT_weights_v2/luotianyi_old-e50.ckpt",
                "G:/Program/zundamonspeech/zundamon-speech-webui/GPT-SoVITS/SoVITS_weights_v2/luotianyi_old_e16_s208.pth",
                "G:/Program/zundamonspeech/zundamon-speech-webui/reference/怎么还是这张图捏，能不能换一张呀.wav",
                "怎么还是这张图捏，能不能换一张呀",
                "zh",
            ),
        }

        self.weight_name = weight_name
        (
            self.gpt_path,
            self.sovits_path,
            self.reference_path,
            self.reference_text,
            self.reference_lang,
        ) = self.weight_path[self.weight_name]

    def set_weights(self):
        """
        加载权重
        """
        url = "http://127.0.0.1:9880/set_gpt_weights"
        data = {"weights_path": self.gpt_path}
        response1 = requests.get(url, params=data)
        url = "http://127.0.0.1:9880/set_sovits_weights"
        data = {"weights_path": self.sovits_path}
        response2 = requests.get(url, params=data)
        print(response1, response2)
        return self

    def __call__(self, text, lang="auto"):
        """
        调用一次生成音频 返回response
        """
        url = "http://127.0.0.1:9880/tts"
        data = {
            "text": text,
            "text_lang": lang,
            "ref_audio_path": self.reference_path,
            "prompt_text": self.reference_text,
            "prompt_lang": self.reference_lang,
        }
        response = requests.get(url, params=data)
        return response

    def save_audio(self, content, path):
        with open(path, "wb") as f:
            f.write(content)

    def generate_audio(self, text, output_path="./test.wav", lang="auto"):
        """
        注意到生成时会莫名加语气词和生成参考文本
        用本办法解决 生成三遍后 挑最短的一个
        但实际上还是会有各种问题 所以建议生成完之后手动调整
        """

        ret = self(text, lang).content
        if len(ret) > 400000:
            ret = self(text, lang).content
            ret2 = self(text, lang).content
            ret3 = self(text, lang).content
            ret = min(ret, ret2, ret3, key=len)
        self.save_audio(ret, output_path)
        return ret


if __name__ == "__main__":
    print(check_voicevox("合併", "がっぺい"))
