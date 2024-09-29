import requests
from lxml import etree
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.26'}







url = 'https://kanji.jitenon.jp/kanji/003'

page_text = requests.get(url=url, headers=headers).text
tree = etree.HTML(page_text)

table = tree.xpath('//*[@id="content"]/article/div[2]/div/div[1]/div[3]/div/section/table/tbody')[0]
trs = table.getchildren()

def extract_text(element):
    # 判断元素是什么类型 如果是<a> 则返回<a>标签中的文本
    if element.tag == 'a':
        return element.xpath('string(.)')
    # 如果是span 则查看里面有没有img
    if element.tag == 'span':
        if element.xpath('img'):
            return element.xpath('img/@alt')[0]
        else:
            return element.xpath('string(.)')
    # 如果是ruby 则返回rb标签中的文本
    if element.tag == 'ruby':
        return element.text

keys = [
    '部首',
    '画数',
    '音読み',
    '訓読み',
    '意味',
    '種別',
    '分類',
    '学年',
    '漢字検定',
    'JIS水準',
]

flag = False
for tr in trs:
    tds = tr.getchildren()
    if len(tds) == 2:
        title = tds[0].xpath('string(.)')
        if title.startswith('意味'):
            flag = True
        print('===' + title + '===')
    texts = etree.tostring(tds[-1], encoding='unicode', method='html')
    # texts = re.sub(r'=".*?"', '', texts)
    texts = re.sub(r'<rt>.*?</rt>', '', texts)
    texts = re.sub(r'/[a-z]', '', texts)
    texts = re.sub(r':/', '', texts)
    texts = re.sub(r'[<>a-z_0123456789="\.#]+', '', texts)
    texts = re.sub(r' +', '', texts)
    
    texts = texts.replace('小学校で習う読み', '【小】 ')
    texts = texts.replace('中学校で習う読み', '【中】 ')
    texts = texts.replace('高校で習う読み', '【高】 ')
    texts = texts.replace('表外読み', '【△】 ')
    texts = texts.replace('１番', '[１] ')
    texts = texts.replace('２番', '[２] ')
    texts = texts.replace('３番', '[３] ')
    texts = texts.replace('４番', '[４] ')
    texts = texts.replace('５番', '[５] ')
    texts = texts.replace('６番', '[６] ')
    texts = texts.replace('７番', '[７] ')
    texts = texts.replace('８番', '[８] ')
    texts = texts.replace('] [', '][')

    if not flag:
        texts = ' '.join(reversed(texts.split(' ')))

    texts = texts.replace('/', ' ')

    print(texts)