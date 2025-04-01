# 约定HtmlPack 生成图片和音频

import os

from html_to_pic import HtmlToPic
from pydub import AudioSegment
from tqdm import tqdm
from voicevox import generate_voicevox, generate_voicevox_check

"""
每一个如下的字典 生成一张图片 给出一段音频
如下的字典叫做一个HtmlPack
{
    "word": "这是要生成的单词"
    "read": "这是提供给voicevox的假名表记 用于初步检查读音"
    "html": "这是要生成的图片的html代码"
}
"""

png_path = "./out/png"
wav_raw_path = "./out/wav_raw"
wav_path = "./out/wav"
err_path = "./out/err.txt"


def htmlpack_process(htmlpack_list):
    """
    传入一个HtmlPack列表
    生成其相应的图片和音频 以及一个初步检查错误的err.txt
    """
    h2p = HtmlToPic()

    if not os.path.exists(png_path):
        os.makedirs(png_path)
    if not os.path.exists(wav_raw_path):  # voicevox直接生成的音频
        os.makedirs(wav_raw_path)

    for i in tqdm(range(len(htmlpack_list))):
        pack = htmlpack_list[i]
        # 生成图片 命名为 index_单词_假名表记.png
        h2p.generate_pic(
            pack["html"], f"{png_path}/{i:04d}_{pack['word']}_{pack['read']}.png"
        )
        # 生成音频 命名为 index_单词_假名表记.wav
        check, voicevox_read = generate_voicevox_check(
            pack["word"],
            pack["read"],
            f"{wav_raw_path}/{i:04d}_{pack['word']}_{pack['read']}.wav",
        )
        if not check:  # not check表示读音不同
            err_msg = f"可能的错误: {i:04d} {pack['word']} => {voicevox_read} 其与 {pack['read']} 不同"
            # print(err_msg)
            with open(err_path, "a", encoding="utf-8") as f:
                # err.txt的格式是 index 单词 假名表记
                f.write(f"{i:04d}\t{pack['word']}\t{pack['read']}\t{voicevox_read}\n")


def replace_err():
    """
    读取修改后的err.txt 使用其中的AquesTalk風記法字符串生成音频并替换原音频
    err.txt的格式应当是 index 单词 假名表记 AquesTalk風記法
    中间用制表符隔开
    """
    with open(err_path, "r", encoding="utf-8") as f:
        err_word = f.readlines()
    err_word = [word.strip().split("\t") for word in err_word]

    for cont in err_word:
        # index 单词 假名表记 AquesTalk風記法
        index_str, word, _, aquestalk = cont

        for filename in os.listdir(wav_raw_path):
            # 找到文件中index相同的那个文件 替换它
            if filename.startswith(index_str):
                print(f"{filename} => {index_str}_{word}_{aquestalk.replace('/','=')}.wav")

                os.remove(os.path.join(wav_raw_path, filename))
                generate_voicevox(
                    word,
                    os.path.join(wav_raw_path, f"{index_str}_{word}_{aquestalk.replace('/','=')}.wav"),
                    aquestalk,
                )
                break


def extend_audio(file_path, file_out_path, target_duration_ms=1500):
    """
    将音频延长到1.5秒 保存到wav_path中
    如果超过了 则不做任何处理
    返回输出音频的时长 单位毫秒
    """

    audio = AudioSegment.from_file(file_path)
    # 音频的时长 单位毫秒
    current_duration = len(audio)

    # 如果音频时长小于目标时长 增加一段静音
    if current_duration < target_duration_ms:
        silence_duration = target_duration_ms - current_duration
        silence = AudioSegment.silent(duration=silence_duration)
        audio_with_silence = audio + silence
    else:
        audio_with_silence = audio
        print(f"音频时长超过目标 {file_path} 当前时长：{current_duration}ms")

    audio_with_silence.export(file_out_path, format="wav")
    return len(audio_with_silence)


def extend_all_audio(target_duration_ms=1500):
    """
    将wav_raw_path中的所有音频延长到1.5秒 保存到wav_path中
    """
    if not os.path.exists(wav_path):
        os.makedirs(wav_path)

    for filename in tqdm(os.listdir(wav_raw_path)):
        if filename.endswith('.wav'):
            extend_audio(os.path.join(wav_raw_path, filename), os.path.join(wav_path, filename), target_duration_ms)
