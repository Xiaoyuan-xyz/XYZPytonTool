# 这是一个自动配中国兔的脚本

from moviepy.video.fx.resize import resize
from moviepy.editor import (
    ImageSequenceClip,
    AudioFileClip,
    CompositeVideoClip,
)
from moviepy.video.io.ffmpeg_writer import ffmpeg_write_video
from pydub import AudioSegment
from imageio import imread

def create_video_clip(audio_path=rf"G:\Program\PytonTool\kanji\videos\output_audio.mp3",
                      video_path=rf"G:\Program\PytonTool\kanji\videos\output_video.mp4"):

    volume_threshold_low = -40
    volume_threshold_high = -30

    audio_clip = AudioSegment.from_file(audio_path)

    image_112 = imread(r"H:\Resource\中国うさぎ立ち素材\1-1-12.png")
    image_113 = imread(r"H:\Resource\中国うさぎ立ち素材\1-1-13.png")
    image_212 = imread(r"H:\Resource\中国うさぎ立ち素材\1-2-12.png")
    image_213 = imread(r"H:\Resource\中国うさぎ立ち素材\1-2-13.png")
    image_312 = imread(r"H:\Resource\中国うさぎ立ち素材\1-3-12.png")
    image_313 = imread(r"H:\Resource\中国うさぎ立ち素材\1-3-13.png")
    image_412 = imread(r"H:\Resource\中国うさぎ立ち素材\1-4-12.png")
    image_413 = imread(r"H:\Resource\中国うさぎ立ち素材\1-4-13.png")

    images = [image_112, image_113, image_212, image_213, image_312, image_313, image_412, image_413]

    interval_duration = 100
    audio_volumes = []
    for i in range(0, len(audio_clip), interval_duration):
        interval = audio_clip[i : i + interval_duration]
        audio_volumes.append(interval.dBFS)
    frames = []
    last_volume = -100
    for volume in audio_volumes:
        if volume > volume_threshold_high:
            frames.append(0)
        elif volume < volume_threshold_low:
            frames.append(1)
        elif volume > last_volume:
            frames.append(0)
        else:
            frames.append(1)
        last_volume = volume

    tick = int(10 * 1000 / interval_duration)
    for i in range(len(frames)// tick - 2):
        frames[i*tick+20] += 2
        frames[i*tick+21] += 4
        frames[i*tick+22] += 6
        frames[i*tick+23] += 4
        frames[i*tick+24] += 2

    frames = frames[:-1]
    frames = [images[i] for i in frames]

    image_clip = ImageSequenceClip(frames, fps=1000 / interval_duration)
    image_clip = resize(image_clip, width=925)

    video = CompositeVideoClip([image_clip.set_position((1300, 405))], size=(1920, 1080))
    video = video.set_audio(AudioFileClip(audio_path))
    ffmpeg_write_video(video, video_path, fps=1000 / interval_duration)

if __name__ == "__main__":
    create_video_clip()
    