# 下载某一年天凤凤凰桌的牌谱

import os
import gzip
import queue
import re
import shutil
import threading
import time

import requests
from urllib3.exceptions import SSLError


def unzip_gz():
    source_directory = './paipu/2022raw/'
    target_directory = './paipu/2022/'
    os.makedirs(target_directory, exist_ok=True)
    prefix = 'scc'
    # sca=個室 / scb=段位戦 / scc=鳳凰卓(牌譜あり) / scd=雀荘戦 / sce=技能戦+琥珀卓(牌譜あり)
    # scaの2カラム目、sc[bcde]の１カラム目は対戦開始時間
    # sc[bcde]の2カラム目はゲーム時間

    files = os.listdir(source_directory)
    scc_files = [file for file in files if file.startswith(prefix)]
    for gz_file in scc_files:
        with gzip.open(os.path.join(source_directory, gz_file), 'rb') as f_in:
            html_file = gz_file.replace('.gz', '')
            with open(os.path.join(target_directory, html_file), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)


HEADER = {'Host': 'e.mjv.jp', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate', 'Connection': 'keep-alive'}


def download_paipu(target_directory, log):
    url = f'https://tenhou.net/0/log/?{log}'
    r = requests.get(url=url, headers=HEADER)
    page_text = r.text
    paipu_path = f'{target_directory}/{log}.xml'
    with open(paipu_path, 'w', encoding='utf-8') as file:
        file.write(page_text)


def consume(queue: queue.Queue):
    while True:
        target_directory, log = queue.get()
        try:
            download_paipu(target_directory, log)
        except Exception as e:
            print(f'{threading.current_thread().name}:{target_directory}/{log} 下载失败')


def download_paipu_in_one_day(file_name, q):
    file_path = f'./paipu/2022/{file_name}.html'
    target_directory = f'./paipu/2022scc/{file_name}/'
    os.makedirs(target_directory, exist_ok=True)

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        pattern = r'四鳳南喰赤.*?log=([^"]+)'
        logs = re.findall(pattern, content)

    files = os.listdir(target_directory)
    if len(files) < len(logs):
        print(f'{file_name}装载任务{len(logs)}')
        for log in logs:
            paipu_path = f'{target_directory}/{log}.xml'
            if os.path.exists(paipu_path):
                continue
            q.put((target_directory, log))


def download_paipu_all():
    q = queue.Queue()
    threads = []
    for i in range(8000):
        t = threading.Thread(target=consume, args=(q,), name=f'consumer{i}')
        t.start()
        threads.append(t)
    files = os.listdir('./paipu/2022/')
    files = files
    for file in files:
        file_name = file[:-5]
        download_paipu_in_one_day(file_name, q)
        # time.sleep(12)
        # print('剩余下载数目：', q.qsize())
    print('任务装载完成')
    while True:
        if q.empty():
            time.sleep(1)
            print('下载完成')
            break
        print('剩余下载数目：', q.qsize())
        time.sleep(1)

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    download_paipu_all()
