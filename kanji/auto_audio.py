# 将目录下的音频拼接成一个音频文件 有空白间隔

from pydub import AudioSegment
import os
from PIL import Image
from moviepy.editor import ImageClip, concatenate_videoclips
from tqdm import tqdm
# 获取当前目录下所有mp3文件
wav_files = [f for f in os.listdir('./kanji/audio/') if f.endswith('.wav')]
wav_files = sorted(wav_files, key=lambda x: os.path.getctime('./kanji/audio/' + x))

output_audio = AudioSegment.silent(duration=2000)
image_clips = []
now_kanji = 0
now_duration = 0

wav_files.append('end')
for file in tqdm(wav_files):
      # 读取音频
    # 添加音频和1秒间隔
    if file == 'end' or int(file.split('_')[0]) > now_kanji:
        output_audio += AudioSegment.silent(duration=4000)
        # image_clips.append(ImageClip(f'./kanji/images/T{now_kanji}.png').set_duration(now_duration / 1000 + 2).set_fps(1))
        now_kanji += 1
        now_duration = 2000
    if file != 'end':
        audio:AudioSegment = AudioSegment.from_file('./kanji/audio/' + file)
        output_audio += audio + AudioSegment.silent(duration=1000)
        now_duration += audio.duration_seconds * 1000 + 1000


output_audio.export("./kanji/videos/output_audio.mp3", format="mp3")

# video = concatenate_videoclips(image_clips, method="compose")
# video = video.set_audio(output_audio)
# video.write_videofile("./kanji/videos/output_video.mp4", fps=1, codec='h264_nvenc', threads=10)

