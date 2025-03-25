from generate_raw import generate_raw

import webbrowser
from parse import load_kanjis
import os
from voicevox import kanji_voicevox

from auto_audio import combine_audio_files
import shutil
from auto_video import create_video_clip
from pydub import AudioSegment
from tqdm import tqdm

all_project = [
    '撃激隙極昔惜籍寂戚積績脊跡夕析席即息 捗勅直適隻斥石赤尺釈式識織拭職植殖食飾',
    '哺捕補舗歩簿部布怖普譜夫扶付府附符腐訃赴父敷膚賦不阜負浮婦富',
    '母募墓慕暮 妬都度渡土吐途塗徒賭図 奴努怒 虜炉賂路露',
    '古故苦枯固錮湖戸顧股孤雇鼓庫呼虎弧互護 儒如乳',
    '柱駐住著貯除 注鋳輸樹朱珠殊諸暑署煮礎疎枢助処初書庶数主',
    '阻祖租組粗塑遡訴素 五悟呉誤汚午 無舞務霧武侮',
    '入 払凸突骨窟出述術卒物',
    '朴僕撲縛副幅福復腹複覆伏服 木牧睦目幕 督篤毒独読 陸録麓',
    '谷穀酷 竹逐築着祝嘱触束属叔淑塾熟 辱 酢蹴宿粛族速足促俗 屋',
    '女 履呂侶旅慮 娯語愚遇隅魚漁御 宇羽雨喩愉諭癒裕与予余誉預',
    '句拘区駆具惧巨拒居距拠挙去虚許 婿狙須緒徐序叙取趣需',
    '率律屈鬱 緑菊局曲畜蓄劇続玉獄域育浴欲',
]

# for i in range(len(all_project)):
#     all_project[i] = all_project[i].replace(' ', '')
#     index = i + 51
#     generate_raw(all_project[i], fr'G:\Project\VideoMake\日语汉字\{index}\raw.md')

# for i in range(len(all_project)):
#     all_project[i] = all_project[i].replace(' ', '')
#     urls = [f'https://www.weblio.jp/content/{it}?dictCode=SGKDJ' for it in all_project[i]]

#     for url in urls:
#         webbrowser.open(url)
#     input()

for i in range(12):
    index = i + 91
    all_project[i] = all_project[i].replace(' ', '')
    path = fr'G:\Project\VideoMake\日语汉字\{index}/'
    
    # 产生voicevox
    ret = []
    for j, it in enumerate(load_kanjis(path + 'raw.md')):
        os.makedirs(path + f'{j}/', exist_ok=True)
        ret1 = kanji_voicevox(j, it, path + f'{j}/')
        ret1 = '\n'.join(ret1)
        ret.append(ret1)
    ret = [it for it in ret if len(it) > 0]
    with open(path + 'ret.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(ret))
    
    # voicevox各自拼在一起
    for j, it in enumerate(load_kanjis(path + 'raw.md')):
        combine_audio_files(path + f'{j}/', path + f'{j}.mp3')

    # 产生图片
    shutil.copyfile(path + 'raw.md', 'G:\Program\PytonTool\kanji/raw.md')
    os.system('G:\Program\PytonTool\kanji\start.bat')
    for j, it in enumerate(load_kanjis(path + 'raw.md')):
        try:
            shutil.move(f'G:\Program\PytonTool\kanji\images\T{j}.png', path+f'T{j}.png')
        except:
            pass

    # 产生总的拼在一起的音频和视频
    wav_files = [f for f in os.listdir(path) if f.endswith('.mp3') and f[0].isdigit()]
    wav_files = sorted(wav_files, key=lambda x: os.path.getctime(path + x))
    output_audio = AudioSegment.silent(duration=0)
    for file in tqdm(wav_files):
        audio:AudioSegment = AudioSegment.from_file(path + file)
        output_audio += audio
    output_audio.export(path + 'output_audio.mp3', format="mp3")
    create_video_clip(path + 'output_audio.mp3', path + 'output_audio.mp4')
