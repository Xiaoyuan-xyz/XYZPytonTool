# 将目录下的音频拼接成一个音频文件 有空白间隔

from pydub import AudioSegment
import os
from tqdm import tqdm
# 获取当前目录下所有mp3文件
wav_files = [f for f in os.listdir('./kanji/audio/') if f.endswith('.wav')]
wav_files = sorted(wav_files, key=lambda x: os.path.getctime('./kanji/audio/' + x)) # 按照创建时间排序

output_audio = AudioSegment.silent(duration=2000)
image_clips = []
now_kanji = 0

wav_files.append('end')
for file in tqdm(wav_files):
    # 读取音频
    # 添加音频和1秒间隔
    if file == 'end' or int(file.split('_')[0]) > now_kanji:
        output_audio += AudioSegment.silent(duration=3000)
        now_kanji += 1
    if file != 'end':
        audio:AudioSegment = AudioSegment.from_file('./kanji/audio/' + file)
        output_audio += audio + AudioSegment.silent(duration=1000)


output_audio.export("./kanji/videos/output_audio.mp3", format="mp3")

