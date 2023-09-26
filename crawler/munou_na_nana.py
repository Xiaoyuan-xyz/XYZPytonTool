import io
import os
import queue
import threading
import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from path_constant import NANA_URL, NANA_PIC_URL

session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57'}

# 根据第一页 获取总页数

options = Options()
# options.add_argument("--headless") # 隐藏浏览器
options.add_experimental_option(
    'excludeSwitches', ['enable-automation'])
options.add_experimental_option(
    'excludeSwitches', ['enable-logging'])
options.add_argument('--incognito')
options.add_argument("disable-cache")
# options.add_argument('--start-maximized')
driver = webdriver.Chrome(options=options)
# ! https://googlechromelabs.github.io/chrome-for-testing/#stable
# ! 这个网址更新chrome driver更快一些


url = 'https://kanbook.net/comic/2244/1/1'


def my_sha2(_0x354253):
    _0x35e93a = 'n-aFeWTsi3BvMK6HtR'
    _0x4dfd81 = '0123456789'
    _0x35e93b = 'juyg71PSrpLcmU5Y2hXOq'
    _0x4dfd82 = 'abcdefghijklmnopqrstuvwxyz'
    _0x35e93c = 'ZCAl4QbDofkGzxd.'
    _0x4dfd83 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _0x4dfd84 = '.-_'
    _0x35e93d = 'JEwN_89I0V'
    _0x35e93e = _0x35e93a + _0x35e93b + _0x35e93c + _0x35e93d
    _0x4dfd85 = _0x4dfd81 + _0x4dfd82 + _0x4dfd83 + _0x4dfd84
    _0x2e7cc6 = ''
    _0x344731 = list(_0x354253)
    for _0x907e75 in range(0xedc28 ^ 0xedc28, len(_0x344731)):
        _0xc6a985 = _0x35e93e.index(_0x344731[_0x907e75])
        _0x2e7cc6 += _0x4dfd85[_0xc6a985]
    return _0x2e7cc6


comic_id = 2244
version_id = 2


# part_id
# page_id

def produce(part_id, queue: queue.Queue):
    url = f'{NANA_URL}/{version_id}/{part_id}'
    driver.get('https://www.baidu.com')
    driver.get(url)
    print(url)
    # input('加载完成后按回车键继续')
    try:
        x_tokens = driver.execute_script('return x_tokens')
    except:
        print('运行时出错，请重新运行')
        while True:
            # 现在的queue没有__len__()实现了？
            print(img_queue.qsize())
            time.sleep(1)
    # print(part_id, x_tokens)

    img_dir = rf'H:\Resource\小说漫画\无能的娜娜\{part_id if version_id == 1 else part_id + 28}'
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)

    for i, img in enumerate(x_tokens):
        queue.put((part_id, i + 1, my_sha2(x_tokens[i])))


def consume(queue: queue.Queue):
    while True:
        part_id, page_id, sha = queue.get()
        img_url = f'{NANA_PIC_URL}/{version_id}/{part_id}/{sha}'
        while True:
            img_data = requests.get(url=img_url, headers=headers).content
            image_b = io.BytesIO(img_data).read()
            size = len(image_b)
            if size > 6656:  # 传输错误是6609
                break
            # time.sleep(1)
        with open(rf'H:\Resource\小说漫画\无能的娜娜\{part_id if version_id == 1 else part_id + 28}\{page_id}.jpg',
                  'wb') as fp:
            fp.write(img_data)


img_queue = queue.Queue()
for i in range(10):
    t = threading.Thread(target=consume, args=(img_queue,), name=f'consumer{i}')
    t.start()

# while True:
# part_id = input('输入part_id')
# if url.startswith('stop'):
#     print('img_queue.qsize(): ', img_queue.qsize())
#     if img_queue.empty():
#         break
#     continue
# part_id = int(part_id)

for part_id in range(61, 62):
    produce(part_id, img_queue)

print('运行结束')
