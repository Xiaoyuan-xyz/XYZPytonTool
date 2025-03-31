import os
import pysrt
import MeCab
from collections import Counter

# 初始化MeCab分词器
mecab = MeCab.Tagger("-Owakati")

def remove_speaker(text):
    """去除括号部分，留下纯日文"""
    import re
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'（.*?）', '', text)
    return text.strip()

def extract_text_from_srt(srt_file):
    """从srt文件中提取日文文本并去除说话人部分"""
    subs = pysrt.open(srt_file)
    text = []
    for sub in subs:
        cleaned_text = remove_speaker(sub.text)
        if cleaned_text:  # 确保文本不为空
            text.append(cleaned_text)
    return text

def tokenize(text):
    """使用MeCab进行分词"""
    return mecab.parse(text).strip().split()

def get_word_frequency(texts):
    """获取词频统计"""
    all_words = []
    for text in texts:
        words = tokenize(text)
        all_words.extend(words)
    return Counter(all_words)

def process_srt_files_in_folder(folder_path):
    """处理文件夹中的所有.srt文件"""
    all_texts = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.srt'):
            srt_file_path = os.path.join(folder_path, filename)
            texts = extract_text_from_srt(srt_file_path)
            all_texts.extend(texts)
    
    word_freq = get_word_frequency(all_texts)
    return word_freq

# 示例：处理一个文件夹中的所有srt文件
folder_path = './kanji_new/steinsgate0'  # 替换为你的文件夹路径
word_freq = process_srt_files_in_folder(folder_path)

# 把这个词频统计保存到文件
with open('./kanji_new/word_freq.txt', 'w', encoding='utf-8') as f:
    for word, freq in word_freq.most_common():
        f.write(f'{word}: {freq}\n')

# 打印前10个最常出现的词汇及其词频
for word, freq in word_freq.most_common():
    print(f'{word}: {freq}')
