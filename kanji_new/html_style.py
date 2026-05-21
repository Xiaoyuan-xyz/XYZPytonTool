# 这个文件接收HtmlPack 从中批量生成图片和音频 不关心其内容和格式 以及最终视频的合成

import os

from htmlpack import ensure_htmlpack_dict
from html_to_pic import HtmlToPic
from pydub import AudioSegment
from tqdm import tqdm
from voicevox import generate_voicevox, generate_voicevox_check

png_path = "./out/png"
wav_raw_path = "./out/wav_raw"
wav_path = "./out/wav"
err_path = "./out/err.txt"


def htmlpack_process_pic(htmlpack_list, *args, **kwargs):
    """
    传入一个 HtmlPack 列表，生成对应图片。

    输出文件名格式：
    index_word_read.png

    注意：当前文件名仍包含原文，方便人工检查；如果之后遇到文件名过长
    或非法字符问题，可以改成 index.png + manifest.json 的方式。
    """
    h2p = HtmlToPic(*args, **kwargs)
    if not os.path.exists(png_path):
        os.makedirs(png_path)
    for i in tqdm(range(len(htmlpack_list))):
        pack = ensure_htmlpack_dict(htmlpack_list[i])
        word = pack["word"]
        read = pack["read"]
        if word is not None:
            word = word.replace("\n", "")
        if read is not None:
            read = read.replace("\n", "")
        # 生成图片 命名为 index_单词_假名表记.png
        h2p.generate_pic(
            pack["html"], f"{png_path}/{i:04d}_{word}_{read}.png"
        )

def htmlpack_process_wav(htmlpack_list):
    """
    传入一个 HtmlPack 列表，生成对应原始音频。

    如果 pack["read"] 不为空，会将人工标注读音和 VOICEVOX 推断读音做
    初步比较；不一致的项目会写入 err.txt，交给用户人工校对。
    """
    if not os.path.exists(wav_raw_path):  # voicevox直接生成的音频
        os.makedirs(wav_raw_path)
    for i in tqdm(range(len(htmlpack_list))):
        pack = ensure_htmlpack_dict(htmlpack_list[i])
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

def htmlpack_process(htmlpack_list):
    """
    传入一个 HtmlPack 列表，同时生成图片和原始音频。

    这个函数适合确认流程稳定后使用。调试阶段建议分别调用
    htmlpack_process_pic() 和 htmlpack_process_wav()，这样更容易定位问题。
    """
    h2p = HtmlToPic()

    if not os.path.exists(png_path):
        os.makedirs(png_path)
    if not os.path.exists(wav_raw_path):  # voicevox直接生成的音频
        os.makedirs(wav_raw_path)

    for i in tqdm(range(len(htmlpack_list))):
        pack = ensure_htmlpack_dict(htmlpack_list[i])
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
    读取人工校对后的 err.txt，使用其中的 AquesTalk 风记法重新生成音频。

    err.txt 的格式应当是：
    index<TAB>单词<TAB>假名表记<TAB>AquesTalk风记法

    中间必须用制表符隔开。
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


def extend_audio(file_path, file_out_path, target_duration_ms=1500, is_append=False):
    """
    将单个音频补静音后保存。

    - is_append=False：只把短于 target_duration_ms 的音频补到目标时长。
    - is_append=True：无论原音频多长，都额外追加 target_duration_ms 的静音。

    返回输出音频的时长，单位毫秒。
    """

    audio = AudioSegment.from_file(file_path)
    # 音频的时长 单位毫秒
    current_duration = len(audio)

    # 如果音频时长小于目标时长 增加一段静音
    if is_append:
        silence_duration = target_duration_ms
        silence = AudioSegment.silent(duration=silence_duration)
        audio_with_silence = audio + silence
    elif current_duration < target_duration_ms:
        silence_duration = target_duration_ms - current_duration
        silence = AudioSegment.silent(duration=silence_duration)
        audio_with_silence = audio + silence
    else:
        audio_with_silence = audio
        print(f"音频时长超过目标 {file_path} 当前时长：{current_duration}ms")

    audio_with_silence.export(file_out_path, format="wav")
    return len(audio_with_silence)


def extend_all_audio(target_duration_ms=1500, is_append=False):
    """
    将 wav_raw_path 中的所有 wav 音频补静音后保存到 wav_path。
    """
    if not os.path.exists(wav_path):
        os.makedirs(wav_path)

    for filename in tqdm(os.listdir(wav_raw_path)):
        if filename.endswith('.wav'):
            extend_audio(os.path.join(wav_raw_path, filename), os.path.join(wav_path, filename), target_duration_ms, is_append)
