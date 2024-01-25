import os
import queue
import re
import threading
import time

import requests
from lxml import etree
from tqdm import tqdm

from path_constant import NANA_RAW_URL, NANA_RAW_PIC_URL

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.26'}

url = NANA_RAW_URL

page_text = requests.get(url=url, headers=headers).text
tree = etree.HTML(page_text)
# # //*[@id="chapterlist"]/ul/li[98]/div/div[2]/a
chapter_as = tree.xpath('//*[@id="chapterlist"]/ul/li/div/div[1]/a')
chapter_as.reverse()

chapter_as = chapter_as[-2:-1]


def consume(queue: queue.Queue):
    while True:
        url = queue.get()
        chapter, page = url.split('/')[-2:]
        page = page.split('-')[0]
        page = page.split('.')[0]
        try:
            page = int(page)
        except:
            print(url)
            continue

        img_data = requests.get(url='https:' + url, headers=headers).content
        with open(rf'H:\Resource\小说漫画\无能的娜娜raw\{chapter}\{page}.jpg', 'wb') as fp:
            fp.write(img_data)


img_queue = queue.Queue()
for i in range(10):
    t = threading.Thread(target=consume, args=(img_queue,), name=f'consumer{i}')
    t.start()

for chapter_a in tqdm(chapter_as):
    url = chapter_a.attrib['href']
    page_text = requests.get(url=url, headers=headers).text

    pattern = f'(//{NANA_RAW_PIC_URL}/.*?\.[wjp](ebp)*(pg)*(ng)*)'
    img_src_list = re.findall(pattern, page_text, re.S)
    # 现在好像把所有地址拿文本形式放在页面最下面了 需要去除\\
    if len(img_src_list) == 0:
        page_text = page_text.replace('\\', '')
        img_src_list = re.findall(pattern, page_text, re.S)

    # 确保文件夹存在
    chapter = img_src_list[0][0].split('/')[-2]
    img_dir = rf'H:\Resource\小说漫画\无能的娜娜raw\{chapter}'
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)

    # 发任务
    for img_src in img_src_list:
        img_queue.put((img_src[0]))

while True:
    if img_queue.empty():
        time.sleep(1)
        print('下载完成')
        break
    print('剩余下载数目：', len(img_queue.queue))
    time.sleep(1)

print('运行完成')

