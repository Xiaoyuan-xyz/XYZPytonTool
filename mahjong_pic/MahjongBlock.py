import re

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

from xyzutil import getHerePath, pathCombine, pathJoin

PILE_WIDTH = 70
PILE_HEIGHT = 100


class MahjongBlockRender:
    '''
    用于处理麻将块的类，支持mpsz 东南西北 空格和文本\\
    ! $换行 * \` 暗色 _ 横置 ^ 双横置 + 牌背 | - 空格
    '''
    # todo 双横置的牌处理不了赤宝牌加杠

    _fontSize = 32
    _fontSizeSmall = 18

    # FONT_PATH = r'C:\Users\Xiaoyuan_xyz\AppData\Local\Microsoft\Windows\Fonts\SourceHanSerifCN-Regular.otf'
    _fontPath = pathCombine(
        (getHerePath(), 'font', 'SourceHanSerifCN-Regular.otf'))
    _fontPathSmall = _fontPath

    # __TEXT_OFFSET = PILE_HEIGHT//2-_fontSize//2-_fontSize//4
    __TEXT_OFFSET = 25  # 26似乎更合适
    __TEXT_OFFSET_SMALL = 3

    @property
    def fontSize(self):
        return self._fontSize

    @fontSize.setter
    def fontSize(self, fontSize):
        self._fontSize = fontSize
        self._font = ImageFont.truetype(self._fontPath, self._fontSize)

    @property
    def fontSizeSmall(self):
        return self._fontSizeSmall

    @fontSizeSmall.setter
    def fontSizeSmall(self, fontSizeSmall):
        self._fontSizeSmall = fontSizeSmall
        self._fontSmall = ImageFont.truetype(
            self._fontPathSmall, self._fontSizeSmall)

    @property
    def fontPath(self):
        return self._fontPath

    @fontPath.setter
    def fontPath(self, fontPath):
        self._fontPath = fontPath
        self._font = ImageFont.truetype(self._fontPath, self._fontSize)

    @property
    def fontPathSmall(self):
        return self._fontPathSmall

    @fontPathSmall.setter
    def fontPathSmall(self, fontPathSmall):
        self._fontPathSmall = fontPathSmall
        self._fontSmall = ImageFont.truetype(
            self._fontPathSmall, self._fontSizeSmall)

    _font = ImageFont.truetype(_fontPath, _fontSize)
    _fontSmall = ImageFont.truetype(_fontPathSmall, _fontSizeSmall)

    @property
    def font(self):
        return self._font

    @property
    def fontSmall(self):
        return self._fontSmall

    __RESOURCE_PATH = pathJoin(getHerePath(), 'assets')

    # TODO: 染红用%表示
    # TODO: 横置牌可以在一行牌的最上方或居中，注意以横置牌开头的场景

    __STRING_MPS = r'(?:\*?[_\^]?(?:\{.*?\})?\d)+[mps]'
    __STRING_Z = r'(?:\*?[_\^]?(?:\{.*?\})?[1-7])+z'
    __STRING_T = r'(?:\d*)(?:\*?[_\^]?)(?:\{.*?\})?[TNR\+东南西北白发中東發発]'
    __STRING_SPACE = r'(?:\d*)[\|-]'
    __STRING_TEXT = r'\[.*?\]'
    __STRING_VAILD = '({})|({})|({})|({})|({})'.format(
        __STRING_MPS, __STRING_Z, __STRING_T, __STRING_SPACE, __STRING_TEXT)
    __PATTERN_VAILD = re.compile(__STRING_VAILD)

    __PATTERN_NUM = re.compile(r'(\*)?([_\^])?(\{.*?\})?(\d)')
    __PATTERN_SPI = re.compile(r'(\d+)?(\*)?([_\^])?(\{.*?\})?')
    __TILE_MAP = {
        '东': (1, 'z'),
        '南': (2, 'z'),
        '西': (3, 'z'),
        '北': (4, 'z'),
        '白': (5, 'z'),
        '发': (6, 'z'),
        '中': (7, 'z'),
        '東': (1, 'z'),
        '發': (6, 'z'),
        '発': (6, 'z'),
        'T': (1, 'z'),
        'N': (2, 'z'),
        'R': (6, 'z'),
        '+': (9, 'z'),
        '|': (0, 'z'),
        '-': (0, 'z'),
    }

    def _getResoucePath(self, name):
        return pathJoin(MahjongBlockRender.__RESOURCE_PATH, name+'.png')

    def getPileImg(self, name):
        return Image.open(self._getResoucePath(name))

    def imgAppend(self, imgList):
        width = 0
        height = 0
        for img in imgList:
            width += img.width
            height = max(height, img.height)
        im = Image.new('RGBA', (width, height))
        width = 0
        for img in imgList:
            im.paste(img, (width, height - img.height))
            width += img.width
        return im

    def imgAppendCol(self, imgList):
        width = 0
        height = 0
        for img in imgList:
            height += img.height
            width = max(width, img.width)
        im = Image.new('RGBA', (width, height))
        height = 0
        for img in imgList:
            im.paste(img, (0, height))
            height += img.height
        return im

    def splitBlock(self, rawStr):
        '''
        把$替换成/ 把\`替换成* 然后按类分块
        '''
        rawStr = rawStr.replace('$', '/')
        # rawStr = rawStr.replace('-', '|')
        rawStr = rawStr.replace('`', '*')

        # 按'/'分行
        rows = rawStr.split(r'/')
        pileSplitRows = []  # 分类好的牌块
        for row in rows:
            # 每行选择出合法的牌块 并分类 需要更多类型时 就在pattern里追加更多
            pileSplitRows.append(
                MahjongBlockRender.__PATTERN_VAILD.findall(row))
        return pileSplitRows

    def vaildCheck(self, rawStr):
        pileSplitRows = self.splitBlock(rawStr)
        safeStrRows = []
        for row in pileSplitRows:
            safeStrRow = ''
            for it in row:
                safeStrRow += ''.join(it)
            safeStrRows.append(safeStrRow)
        return '$'.join(safeStrRows)

    def generateImg(self, pileSplitRows):
        imgRows = []
        for row in pileSplitRows:
            imgs = []
            for block in row:
                imgs.append(self.parseBlock(block))
            imgRows.append(imgs)
        outs = []
        for imgRow in imgRows:
            outs.append(self.imgAppend(imgRow))
        return self.imgAppendCol(outs)

    def drawMahjong(self, rawStr):
        '''
        处理字符串，返回图片
        '''
        pileSplitRows = self.splitBlock(rawStr)
        img = self.generateImg(pileSplitRows)
        return img

    def parseBlock(self, block):
        indexBlock = block[0]+block[1]  # mpsz
        repeatBlock = block[2]+block[3]  # 特殊 空格
        textBlock = block[4]  # 文本
        if indexBlock != '':
            type = indexBlock[-1]  # 类型 mpsz
            piles = MahjongBlockRender.__PATTERN_NUM.findall(indexBlock)
            imgs = []
            for pile in piles:
                img = self.processSingle(pile[0] == '*' or pile[0] == '`',
                                         pile[1] == '_', pile[1] == '^', pile[3], type, pile[2])
                imgs.append(img)
            img = self.imgAppend(imgs)
        if repeatBlock != '':
            spitype = repeatBlock[-1]  # 特殊类型
            (index, type) = MahjongBlockRender.__TILE_MAP[spitype]  # 转换为 编号和类型
            piles = MahjongBlockRender.__PATTERN_SPI.findall(repeatBlock)
            if len(piles) == 0:
                repeatBlock = repeatBlock[:-1]
                repeatBlock = repeatBlock + '1'  # 没有数字时在后面补个1
                piles = MahjongBlockRender.__PATTERN_SPI.findall(repeatBlock)
            pile = piles[0]
            img = self.processSingle(pile[1] == '*' or pile[1] == '`', pile[2]
                                     == '_', pile[2] == '^', str(index), type, pile[3])
            times = 1 if pile[0] == '' else int(pile[0])
            times = 140 if times > 140 else times
            times = 14 if times > 14 and index != 9 else times
            img = self.imgAppend([img]*times)
        if textBlock != '':  # 牌内字符 用[]括起
            text = textBlock[1:-1]
            # TODO: 想办法允许字串的高度不必是牌的高度
            color, text = self._getTextColor(text)
            img = self.drawText(text, self.font, (0, MahjongBlockRender.__TEXT_OFFSET), color=color,
                                minHeight=PILE_HEIGHT)
        return img

    def _getTextColor(self, text, symbol='#'):
        '''
        如果以#FFFFF类似的结尾，删去，返回颜色元组，否则返回黑色
        '''
        color = [0, 0, 0]
        if len(text) >= 7 and text[-7] == symbol:
            color[0] = int(text[-6:-4], 16)
            color[1] = int(text[-4:-2], 16)
            color[2] = int(text[-2:], 16)
            text = text[:-7]
        return tuple(color), text

    def processSingle(self, shadow, sideway, Wsideway, index, type, text):
        '''
        绘制一张牌
        '''
        # print('阴影:{} 横置:{} 双横置:{} {}{}'.format(shadow, sideway, Wsideway, num, type))
        img = self.getPileImg(index+type)
        if sideway:
            img = img.transpose(Image.Transpose.ROTATE_90)
        if Wsideway:
            img = img.transpose(Image.Transpose.ROTATE_90)
            img = self.imgAppendCol([img]*2)
        if shadow:
            brightEnhancer = ImageEnhance.Brightness(img)
            img = brightEnhancer.enhance(0.6)
        if text != '':  # 附在图片上方的字 用{}括起
            text = text[1:-1]
            color, text = self._getTextColor(text)
            (width, height) = self._fontSmall.getsize(text)
            textImg = Image.new(
                'RGBA', (PILE_WIDTH, height+MahjongBlockRender.__TEXT_OFFSET_SMALL))
            draw = ImageDraw.Draw(textImg)
            draw.text(((img.width-width)/2, 0), text,
                      color, font=self._fontSmall)
            img = self.imgAppendCol([textImg, img])
        return img

    def drawText(self, text, font, position=(0, 0), color=(0, 0, 0), minWidth=0, minHeight=0):
        (_, _, width, height) = font.getbbox(text)
        width = width if minWidth < width else minWidth
        height = height if minHeight < height else minHeight
        img = Image.new('RGBA', (width, height))
        draw = ImageDraw.Draw(img)
        draw.text(position, text, color, font=font)
        return img


if __name__ == '__main__':

    mbr = MahjongBlockRender()

    allPiles = '222216666p222216666m/333317777p333317777m/444418888p444418888m/555519999p555519999m/1111z0m6666z222216666s/2222z0p7777z333317777s/3333z0p++++444418888s/4444z0s5555z555519999s'
    rawStr = '7+'

    # |摸牌 10|副露|副露 |||文字|
    outfilepath = r'H:\Life\Project\markdown\mahjong\temp'
    # outfilepath = r'D:\Life\Project\markdown\mahjong\何切记忆\assets'
    # outfilepath = r'D:\Life\Project\markdown\mahjong\绝对手顺\assets'
    while True:
        rawStr = input('输入序列')
        outpath = pathJoin(outfilepath, rawStr+'.png')
        img = mbr.drawMahjong(rawStr)
        img.show()
        img.save(outpath)
