# 这是一个自动配中国兔的脚本

import matplotlib.pyplot as plt
from moviepy.video.fx.resize import resize
from moviepy.editor import (
    VideoFileClip,
    ImageClip,
    clips_array,
    ImageSequenceClip,
    AudioFileClip,
    CompositeVideoClip,
)
from moviepy.video.io.ffmpeg_writer import ffmpeg_write_video
from pydub import AudioSegment
from imageio import imread

audio_index = 12

# video_path = r"G:\Project\VideoMake\日语汉字学习\0\TextExample.mp4"
# video_clip = VideoFileClip(video_path)
volume_threshold = -35
audio_clip = AudioSegment.from_file(
    rf"G:\Project\VideoMake\日语汉字学习\{audio_index}\audio.mp3"
)
# image_a = ImageClip(r'H:\Resource\中国うさぎ立ち素材\1-1-12.png', transparent=True)
# image_b = ImageClip(r'H:\Resource\中国うさぎ立ち素材\1-1-13.png', transparent=True)
image_a = imread(
    r"H:\Resource\中国うさぎ立ち素材\1-1-12.png",
)
image_b = imread(r"H:\Resource\中国うさぎ立ち素材\1-1-13.png")

# alpha = 0.4
# image_a[:,:,3]  = image_a[:,:,3]*alpha
# image_b[:,:,3] = image_b[:,:,3]*alpha

interval_duration = 100
audio_volumes = []
for i in range(0, len(audio_clip), interval_duration):
    interval = audio_clip[i : i + interval_duration]
    audio_volumes.append(interval.dBFS)
frames = []
for volume in audio_volumes:
    if volume > volume_threshold:
        frames.append(image_a)
    else:
        frames.append(image_b)

image_clip = ImageSequenceClip(frames, fps=1000 / interval_duration)
image_clip = resize(image_clip, width=925)

# video_mask = ImageSequenceClip(masks, fps=1000/interval_duration,  ismask=True)
# video_clip = video_clip.set_mask(video_mask)

# video = CompositeVideoClip([video_clip,image_clip.set_position((2600, 810))])
video = CompositeVideoClip([image_clip.set_position((1300, 405))], size=(1920, 1080))
video = video.set_audio(
    AudioFileClip(rf"G:\Project\VideoMake\日语汉字学习\{audio_index}\audio.mp3")
)
ffmpeg_write_video(
    video,
    rf"G:\Project\VideoMake\日语汉字学习\{audio_index}\audio.mp4",
    fps=1000 / interval_duration,
)
