import re
from collections import Counter

from matplotlib import pyplot as plt
from pypinyin import pinyin, Style

import os
import glob

from tqdm import tqdm

if  __name__ == '__main__':
    path = './data/ToRCH2019/ToRCH2019_V1.5/*.txt'
    txt_files = glob.glob(path)

    counts = Counter('')

    # 遍历每个文件并读取内容
    for txt_file in tqdm(txt_files):
        with open(txt_file, 'r', encoding='utf-8') as file:
            content = file.read()
            content = re.findall('[\u4e00-\u9fa5]', content)
            content = ''.join(content)
            content = pinyin(content, style=Style.TONE3)
            content = [it[0] for it in content]
            count = Counter(content)
            counts += count

    counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    print(counts)
    elements, counts = zip(*counts)
    total_counts = sum(counts)
    percentage_counts = [count / total_counts * 100 for count in counts]

    # 绘制分布图
    plt.plot(range(len(elements)), counts, color='skyblue')
    plt.xlabel('Element')
    plt.ylabel('Count')
    plt.title('Element Distribution')
    plt.grid()
    plt.loglog()
    plt.show()

    # 计算累积频率
    cumulative_counts = [sum(counts[:i + 1]) for i in range(len(counts))]
    cumulative_percentage = [sum(percentage_counts[:i + 1]) for i in range(len(percentage_counts))]

    # 绘制累积分布折线图
    plt.plot(range(len(elements)), cumulative_percentage)
    plt.xlabel('Element')
    plt.ylabel('Cumulative Count')
    plt.title('Cumulative Distribution')
    plt.loglog()
    plt.grid()
    plt.show()