# 将目录下的音频拼接成一个音频文件 有空白间隔

from pydub import AudioSegment
import os
from tqdm import tqdm


def combine_audio_files(wav_files_path, path="./kanji/videos/output_audio.mp3"):
    wav_files = [f for f in os.listdir(wav_files_path) if f.endswith('.wav')]
    wav_files = sorted(wav_files, key=lambda x: os.path.getctime(wav_files_path + x))
    output_audio = AudioSegment.silent(duration=1000) # 2000
    now_kanji = 0

    wav_files.append('end')
    for file in tqdm(wav_files):
        # 读取音频
        # 添加音频和1秒间隔
        if file == 'end' or int(file.split('_')[0]) > now_kanji:
            output_audio += AudioSegment.silent(duration=100) # 3000
            now_kanji += 1
        if file != 'end':
            audio:AudioSegment = AudioSegment.from_file(wav_files_path + file)
            output_audio += audio + AudioSegment.silent(duration=1000) # 1000


    output_audio.export(path, format="mp3")


if __name__ == '__main__':
    combine_audio_files('./kanji/audio/')
