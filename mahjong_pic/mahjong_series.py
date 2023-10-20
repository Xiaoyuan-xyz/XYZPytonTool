# 由于之前代码的混乱 这里重新写一下需求分析
# 这个文件是用于生成麻将图片的 其可以处理常见的麻将字符串

'''
最简单的是门清字符串
147m223s

标准格式在门清字符串上多以下功能
_ w表示横置 _()表示将括号内的部分全部横置
^x表示 _(xx) 即双横置
=()表示叠放

丰富格式又多以下功能
` 表示暗色
% 表示红色
$ 表示换行
[]表示里面的字
[#FFF]表示字的颜色
[@]表示居中在牌的宽度上
- 表示1/10张牌宽度的空格
, 表示1张牌宽度 1/10张牌高度的空格
+ 表示牌背
这三项可以用前加次数表示重复

koba何切格式
p22z22p7,m550=5,s5550,p550+5
何切格式不是随意的 需要麻将规则来保证

koba牌画格式
{s067z1 z1}(ツモ) {p2-13} {z66=6-6} {_z77_} {  }(ドラ){m1}
空格为空
-表示横置
=表示杠 5=0-时 宝牌在
_表示牌背

tenhou0格式
0-135表示牌 其中赤宝牌是第一张

tenhou0副露格式
就是个数字

tenhou6格式
11-19是万子 10是0m
41-47是字牌

windows系统里文件名不能包含
\  /  :  *  ?  "  <  >  |
'''
import functools
import os
import re

import numpy as np
from PIL import Image, ImageEnhance, ImageMath


def tile_compare(a, b):
    na, sa = a
    nb, sb = b
    suits = {'m': 1, 'p': 2, 's': 3, 'z': 4}
    sa = suits[sa]
    sb = suits[sb]
    number = {'0': 10, '1': 1, '2': 2, '3': 3, '4': 4, '5': 15, '6': 16, '7': 17, '8': 18, '9': 19}
    na = number[na]
    nb = number[nb]
    if sa > sb:
        return 1
    elif sa < sb:
        return -1
    else:
        if na > nb:
            return 1
        elif na < nb:
            return -1
        else:
            return 0


class MahjongSeries:
    """
    麻将序列 用于绘制门清字符串
    内部是一个麻将牌序列

    >>> m = MahjongSeries()
    >>> m.from_tenhou('03m2235s88z0246p')
    >>> m.series
    ['0m', '3m', '2s', '2s', '3s', '5s', '0p', '2p', '4p', '6p']
    >>> m.sort()
    >>> m.series
    ['3m', '0m', '2p', '4p', '0p', '6p', '2s', '2s', '3s', '5s']
    >>> m
    30m2406p2235s
    >>> m.to_koba()
    'm30p2406s2235'
    >>> m.to_discrete_str()
    '3m0m2p4p0p6p2s2s3s5s'
    >>> m.from_tenhou0([103,91,51,39,18,59,57,14,16,108,92,89,105])
    >>> m.sort()
    >>> m.to_tenhou()
    '405m1466p55689s1z'
    >>> m.from_tenhou6([15, 10, 25, 20, 13, 11, 19, 42, 47, 30])
    >>> m.sort()
    >>> m.to_tenhou()
    '13059m05p0s27z'
    >>> m.to_tenhou6()
    [11, 13, 10, 15, 19, 20, 25, 30, 42, 47]
    """

    def __init__(self):
        self.series = []

    def from_tenhou(self, mahjong_str):
        self.series = []
        pattern = re.compile('[0-9]+[mps]|[1-7]+z')
        suits_series = pattern.findall(mahjong_str)
        for suit_series in suits_series:
            suit = suit_series[-1]
            for n in suit_series[:-1]:
                self.series.append(n + suit)

    def from_koba(self, mahjong_str):
        self.series = []
        pattern = re.compile('[mps][0-9]+|z[1-7]+')
        suits_series = pattern.findall(mahjong_str)
        for suit_series in suits_series:
            suit = suit_series[0]
            for n in suit_series[1:]:
                self.series.append(n + suit)

    def from_tenhou0(self, arr):
        self.series = []
        for it in arr:
            s = it // 36
            n = (it % 36) // 4 + 1
            n = 0 if n == 5 and it % 4 == 0 else n
            self.series.append(str(n) + 'mpsz'[s])

    def from_tenhou6(self, arr):
        self.series = []
        for it in arr:
            s = it // 10 - 1
            n = it % 10
            self.series.append(str(n) + 'mpsz'[s])

    def sort(self):
        self.series.sort(key=functools.cmp_to_key(tile_compare))

    def to_discrete_list(self):
        return self.series

    def to_discrete_str(self):
        return ''.join(self.series)

    def to_tenhou(self):
        ret = []
        suit = ''
        for it in self.series[::-1]:
            n, s = it
            if s != suit:
                suit = s
                ret.append(s)
            ret.append(n)
        ret.reverse()
        return ''.join(ret)

    def to_koba(self):
        ret = []
        suit = ''
        for it in self.series:
            n, s = it
            if s != suit:
                suit = s
                ret.append(s)
            ret.append(n)
        return ''.join(ret)

    def to_tenhou6(self):
        ret = []
        suits = {'m': 1, 'p': 2, 's': 3, 'z': 4}
        for it in self.series:
            n, s = it
            ret.append(suits[s] * 10 + int(n))
        return ret

    def __str__(self):
        return self.to_tenhou()

    def __repr__(self):
        return self.to_tenhou()


class MahjongBlock:
    '''
    >>> m=MahjongBlock()
    >>> m.parse('25z10---$4`%2`6p13-3+,2,455_(33)m_(3440)p__(224)m33^4s1_234^5__(6)`%_7=(89)_(01)`2%3`%45%0_(`6%7`%8)9m').series
    ['25z', '10-', '-', '-', '4`%2`6p', '13-', '3+', ',', '2,', '455_(33)m', '_(3440)p', '__(224)m', '33^4s', '1_234^5__(6)`%_7=(89)_(01)`2%3`%45%0_(`6%7`%8)9m']

    '''
    def __init__(self):

        self.IMG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets')

        self.series = []
        self.string = ''

        pattern1 = '((`?%?_?[0-9])+|(_{1,2}|=)\((`?%?[0-9])+\)|\^[0-9])+[mps]'
        pattern2 = '((`?%?_?[1-7])+|(_{1,2}|=)\((`?%?[1-7])+\)|\^[1-7])+[z]'
        pattern3 = '[\d]*[\+,-]'
        pattern = f'({pattern1})|({pattern2})|({pattern3})'
        self.pattern = re.compile(pattern)

    def parse(self, mahjong_str):
        """
        解析字符串
        """
        b = self.pattern.findall(mahjong_str)
        self.series = []
        for it in b:
            if it[0] != '':
                self.series.append(it[0])
            if it[5] != '':
                self.series.append(it[5])
            if it[10] != '':
                self.series.append(it[10])
        self.string = ''.join(self.series)
        return self

    def get_tile_image(self, string):
        """
        根据名字 获取单张牌的图片
        """
        if string == '+':
            return Image.open(os.path.join(self.IMG_PATH, '9z.png'))
        elif string == '-':
            return Image.open(os.path.join(self.IMG_PATH, '0z.png'))
        elif string == ',':
            return Image.open(os.path.join(self.IMG_PATH, '8z.png'))
        else:
            return Image.open(os.path.join(self.IMG_PATH, f'{string}.png'))

    def _generate_easy_image(self):
        """
        只生成水平方向上的牌谱序列
        """


    def generate_block(self, it):
        """
        生成单色牌对应的序列 返回一个图片列表
        """
        suit = it[-1]
        if suit == '+' or suit == ',' or suit == '-':
            times = 1
            if len(it) > 1:
                times = int(it[:-1])
            imgs = [self.get_tile_image(suit)] *  times
        else:
            imgs = []
            dark = False
            red = False
            rotate = False
            clock_rotate = False
            sub_sequence = False
            double = False
            rotate_imgs = []
            for char in it[:-1]:
                if char == '`':
                    dark = True
                elif char == '%':
                    red = True
                elif char == '^':
                    double = True
                elif char == '_':
                    if rotate:
                        rotate = False
                        clock_rotate = True
                    else:
                        rotate = True
                elif char == '=':
                    pass # 知道在子序列里就够了
                elif char == '(':
                    sub_sequence = True
                elif char in '0123456789':
                    single_image =  self.get_tile_image(char + suit)
                    if dark:
                        dark = False
                        brightEnhancer = ImageEnhance.Brightness(single_image)
                        single_image = brightEnhancer.enhance(0.6)
                    if red:
                        red = False
                        width, height = single_image.size
                        for i in range(width):
                            for j in range(height):
                                r, g, b, a = single_image.getpixel((i, j))
                                r = int(r * 0.87)
                                g = int(g * 0.68)
                                b = int(b * 0.68)
                                single_image.putpixel((i, j), (r, g, b, a))
                    if double:
                        double = False
                        single_image = single_image.transpose(Image.ROTATE_90)
                        single_image = self.image_join_vertical([single_image]*2)
                    if rotate:
                        single_image = single_image.transpose(Image.ROTATE_90)
                    if clock_rotate:
                        single_image = single_image.transpose(Image.ROTATE_270)
                    if sub_sequence: # 子序列
                        rotate_imgs.append(single_image)
                    else: # 不是子序列的话 rotate只适用一张牌
                        rotate = False
                        imgs.append(single_image)
                elif char == ')':
                    rotate = False
                    clock_rotate = False
                    sub_sequence = False
                    imgs.append(self.image_join_vertical(rotate_imgs))
                    rotate_imgs = []
        return imgs


    def image_join(self, image_list):
        """
        把一个图片列表水平拼接
        """
        width = 0
        height = 0
        for img in image_list:
            width += img.width
            height = max(height, img.height)
        im = Image.new('RGBA', (width, height))
        width = 0
        for img in image_list:
            im.paste(img, (width, height - img.height))
            width += img.width
        return im

    def image_join_vertical(self, image_list, top_to_down = False):
        """
        把一个图片列表竖直拼接
        """
        top_to_down = 1 if top_to_down else -1
        width = 0
        height = 0
        for img in image_list:
            height += img.height
            width = max(width, img.width)
        im = Image.new('RGBA', (width, height))
        height = 0
        for img in image_list[::top_to_down]:
            im.paste(img, (0, height))
            height += img.height
        return im


    def generate_image(self):
        """
        生成对应的图片
        """
        img_list = []
        for it in self.series:
            it = self.generate_block(it)
            img_list.extend(it)
        return self.image_join(img_list)

if __name__ == "__main__":
    m = MahjongBlock()
    m.parse('25z10---$4`%2`6p13-3+,2,455_(33)m_(3440)p__(224)m33^4s1_234^5__(6)`%_7=(89)_(01)`2%3`%45%0_(`6%7`%8)9m')
    print(m.series)
    m.generate_image().show()



