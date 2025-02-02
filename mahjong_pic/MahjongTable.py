import re

from PIL import Image, ImageDraw, ImageFont

from MahjongBlock import MahjongBlockRender
from mahjong_series import MahjongBlock

PILE_WIDTH = 70
PILE_HEIGHT = 100

FONT_SIZE_SYMBOL = 100  # 东南西北四个大字
FONT_SIZE_TENBOU = 60  # 点数
FONT_SIZE_KYOKU = 108  # 局数
FONT_SIZE_HONBA = 60  # 本场和供托

FONT_PATH_BOLD = r'C:\Users\XiaoyuanXYZ\AppData\Local\Microsoft\Windows\Fonts\SourceHanSerifCN-Bold.otf'
FONT_PATH_REGULAR = r'C:\Users\XiaoyuanXYZ\AppData\Local\Microsoft\Windows\Fonts\SourceHanSerifCN-Regular.otf'

FONT_SYMBOL = ImageFont.truetype(FONT_PATH_BOLD, FONT_SIZE_SYMBOL)
FONT_TENBOU = ImageFont.truetype(FONT_PATH_BOLD, FONT_SIZE_TENBOU)
FONT_KYOKU = ImageFont.truetype(FONT_PATH_BOLD, FONT_SIZE_KYOKU)
FONT_HONBA = ImageFont.truetype(FONT_PATH_BOLD, FONT_SIZE_HONBA)


class MahjongTable:
    kyoku = 0  # 局数
    honnba = 0  # 本场
    riichibou = 0  # 立直棒
    dora = ''  # 宝牌
    wannpai = '5+'  # 宝牌指示牌
    jika = 0  # 视角
    symbol = ['東', '南', '西', '北']

    # 这些列表是按照自家 下家 对家 上家的顺序进行的
    pai = ['', '', '', '']
    river = ['', '', '', '']
    tenbou = [25000, 25000, 25000, 25000]
    player_info = ['', '', '', '']
    mid_text = ['', '', '', '']

    def generateImg(self):
        SIZE = 22 * PILE_WIDTH  # 桌子的大小
        SIZE_CENTER = 8 * PILE_WIDTH  # 中间信息区的大小
        CENTER_BORDER = 20  # 东南西北以及点数和边框的距离
        TABLE_BORDER = 20  # 手牌和牌桌边缘的距离
        RIVER_BORDER = 15  # 牌河和信息框的距离

        # 本场和场供中间间隔的距离的一半
        HALF_HONBA_RIICHI_DISTANCE = 5
        # 局数距离中线往左偏的距离 局数中线到信息区上沿的距离
        KYOKU_OFFSET = (-5, 200)
        # 本场、场供距离中线往右偏的距离
        HONBA_RIICHI_OFFSET = 55
        # 本场距离中线往右偏的距离 本场下边沿的的距离
        HONBA_OFFSET = (HONBA_RIICHI_OFFSET,
                        KYOKU_OFFSET[1]-HALF_HONBA_RIICHI_DISTANCE)
        # 场供距离中线往右偏的距离 场供上边沿的的距离
        RIICHI_OFFSET = (HONBA_RIICHI_OFFSET,
                         KYOKU_OFFSET[1]+HALF_HONBA_RIICHI_DISTANCE)

        DORA_POSITION = (SIZE//2, SIZE//2+50)  # 宝牌的位置的上中心点

        COLOR_TABLE = (0, 128, 0, 255)  # 桌布颜色
        COLOR_CENTER = (153, 153, 153)  # 信息区颜色
        COLOR_OUTLINE = (37, 37, 37)  # 信息区边框颜色
        OUTLINE_WIDTH = 4  # 信息区边框宽度

        CENTER_L = (SIZE-SIZE_CENTER)//2
        CENTER_R = (SIZE+SIZE_CENTER)//2

        img = Image.new('RGBA', (SIZE, SIZE), color=COLOR_TABLE)
        mbr = MahjongBlock()
        mbr_old = MahjongBlockRender()
        draw = ImageDraw.Draw(img)
        draw.rectangle((CENTER_L, CENTER_L, CENTER_R, CENTER_R),
                       fill=COLOR_CENTER, outline=COLOR_OUTLINE, width=OUTLINE_WIDTH)

        SYMBOLS_POSITION = [
            (CENTER_L+CENTER_BORDER,
             CENTER_R-CENTER_BORDER-FONT_SIZE_SYMBOL),
            (CENTER_R-CENTER_BORDER-FONT_SIZE_SYMBOL,
             CENTER_R-CENTER_BORDER-FONT_SIZE_SYMBOL),
            (CENTER_R-CENTER_BORDER-FONT_SIZE_SYMBOL,
             CENTER_L+CENTER_BORDER),
            (CENTER_L+CENTER_BORDER,
             CENTER_L+CENTER_BORDER)]
        TENBOU_POSITION = [
            (SIZE//2, CENTER_R-CENTER_BORDER),
            (CENTER_R-CENTER_BORDER, SIZE//2),
            (SIZE//2, CENTER_L+CENTER_BORDER),
            (CENTER_L+CENTER_BORDER, SIZE//2),
        ]
        TENBOU_OFFSET = [(-1, -2), (-2, -1), (-1, 0), (0, -1)]
        PAI_POSITION = [
            (SIZE//2, SIZE-TABLE_BORDER),
            (SIZE-TABLE_BORDER, SIZE//2),
            (SIZE//2, TABLE_BORDER),
            (TABLE_BORDER, SIZE//2),
        ]
        RIVER_POSITION = [
            (SIZE//2-3*PILE_WIDTH, CENTER_R+RIVER_BORDER),
            (CENTER_R+RIVER_BORDER, SIZE//2+3*PILE_WIDTH),
            (SIZE//2+3*PILE_WIDTH, CENTER_L-RIVER_BORDER),
            (CENTER_L-RIVER_BORDER, SIZE//2-3*PILE_WIDTH),
        ]
        RIVER_OFFSET = [(0, 0), (0, -1), (-1, -1), (-1, 0)]
        for i in range(4):
            me = (self.jika+i) % 4  # 当前家的编号

            # 东南西北四个字
            symbol = self.symbol[me]
            (_, _, textWidth, textHeight) = FONT_SYMBOL.getbbox(symbol)
            # textWidth == FONT_SIZE_SYMBOL, textHeight比FONT_SIZE_SYMBOL稍大 好像是4:5
            symbolImg = Image.new('RGBA', (FONT_SIZE_SYMBOL, FONT_SIZE_SYMBOL))
            symbolDraw = ImageDraw.Draw(symbolImg)
            symbolDraw.text((0, textWidth-textHeight), symbol,
                            (0, 0, 0), font=FONT_SYMBOL)
            symbolImg = symbolImg.rotate(i*90)
            (symbolWidth, symbolHeight) = symbolImg.size
            img.paste(
                symbolImg, SYMBOLS_POSITION[i], mask=symbolImg.split()[3])

            # 点数
            tenbou = str(self.tenbou[i])
            (_, _, textWidth, textHeight) = FONT_TENBOU.getbbox(tenbou)
            tenbouImg = Image.new('RGBA', (textWidth, textHeight))
            tenbouDraw = ImageDraw.Draw(tenbouImg)
            tenbouDraw.text((0, 0), tenbou, (0, 0, 0), font=FONT_TENBOU)
            if i != 0:
                tenbouImg = tenbouImg.transpose(Image.ROTATE_90+i-1)
            (tenbouWidth, tenbouHeight) = tenbouImg.size
            img.paste(tenbouImg, (TENBOU_POSITION[i][0]+TENBOU_OFFSET[i][0]*tenbouWidth//2,
                      TENBOU_POSITION[i][1]+TENBOU_OFFSET[i][1]*tenbouHeight//2), mask=tenbouImg.split()[3])

            # 手牌
            paiImg = mbr.parse(self.pai[i]).generate_image()
            if i != 0:
                paiImg = paiImg.transpose(Image.ROTATE_90+i-1)
            (paiWidth, paiHeight) = paiImg.size
            img.paste(paiImg, (PAI_POSITION[i][0]+TENBOU_OFFSET[i][0]*paiWidth//2,
                      PAI_POSITION[i][1]+TENBOU_OFFSET[i][1]*paiHeight//2), mask=paiImg.split()[3])
            # todo 手牌不应该居中 摸牌不应该更改手牌位置 副露应该放在最右边

            # 牌河
            riverImg = mbr_old.drawMahjong(self.river[i])
            if i != 0:
                riverImg = riverImg.transpose(Image.ROTATE_90+i-1)
            (riverWidth, riverHeight) = riverImg.size
            img.paste(riverImg, (RIVER_POSITION[i][0]+RIVER_OFFSET[i][0]*riverWidth,
                      RIVER_POSITION[i][1]+RIVER_OFFSET[i][1]*riverHeight), mask=riverImg.split()[3])

        # 局数
        kyoku = '{}{}'.format(self.symbol[self.kyoku//4], self.kyoku % 4+1)
        (_, _, kyokuWidth, kyokuHeight) = FONT_KYOKU.getbbox(kyoku)
        draw.text((SIZE//2-KYOKU_OFFSET[0]-kyokuWidth, CENTER_L +
                  KYOKU_OFFSET[1]+FONT_SIZE_KYOKU//2-kyokuHeight), kyoku, (0, 0, 0), font=FONT_KYOKU)

        # 本场
        honba = '{}本'.format(self.honba)
        (_, _, honbaWidth, honbaHeight) = FONT_HONBA.getbbox(honba)
        draw.text((SIZE//2+HONBA_OFFSET[0], CENTER_L +
                  HONBA_OFFSET[1]-honbaHeight), honba, (0, 0, 0), font=FONT_HONBA)

        # 场供
        riichi = '{}供'.format(self.riichibou)
        (_, _, riichiWidth, riichiHeight) = FONT_HONBA.getbbox(riichi)
        draw.text((SIZE//2+RIICHI_OFFSET[0], CENTER_L + RIICHI_OFFSET[1] -
                  riichiHeight+FONT_SIZE_HONBA), riichi, (0, 0, 0), font=FONT_HONBA)

        if self.dora == '':
            doraImg = mbr.parse(self.wannpai).generate_image()
        else:
            dora = '[ドラ]-{}'.format(self.dora)
            doraImg = mbr_old.drawMahjong(dora)
        (doraWidth, doraHeight) = doraImg.size
        img.paste(doraImg, (DORA_POSITION[0]-doraWidth //
                  2, DORA_POSITION[1]), mask=doraImg.split()[3])

        return img

    def fromEasyStr(self, easyStr):
        # 场 本 供 视角 dora 点数
        stringEasyStr = r'\((\d*),(\d*),(\d*),([0-3]?),(.*?),(\d*),(\d*),(\d*),(\d*)\)\((.*?)\)\((.*?)\)'
        match = re.match(stringEasyStr, easyStr)
        self.kyoku = match.group(1)
        self.kyoku = 0 if self.kyoku == '' else int(self.kyoku)
        self.honba = match.group(2)
        self.honba = 0 if self.honba == '' else int(self.honba)
        self.riichibou = match.group(3)
        self.riichibou = 0 if self.riichibou == '' else int(self.riichibou)
        self.jika = match.group(4)
        self.jika = 0 if self.jika == '' else int(self.jika)
        self.dora = match.group(5)
        for i in range(4):
            self.tenbou[i] = match.group(6+i)
            self.tenbou[i] = '' if self.tenbou[i] == '' else 100 * \
                int(self.tenbou[i])
        self.pai = match.group(10).split(',')
        l = len(self.pai)
        for i in range(l, 4):
            self.pai.append('13+')
        self.river = match.group(11).split(',')
        l = len(self.river)
        for i in range(l, 4):
            self.river.append('')


if __name__ == "__main__":

    table = MahjongTable()
    table.fromEasyStr('(0,0,2,1,4z,240,250,240,250)(123456789m50p67s,788p33556s22z10-44_4z,123345m123p0789s,666m5s10-1_11z9_99p22_2s)(7z1p2p`7z`4z1s$1s2m_4p,7m9s4p`2p5z`8s$`2s6p,8m5z5p`_8p`7m`6z$`5m,3z7z8m5z6z`3p$8p4s`2m`1s`8s)')
    table.fromEasyStr('(4,0,1,1,2p,182,179,318,311)(579m23567889p66z-6z)(423z91s5z$6s21m3p5z,1p17z4s99p$1p3z1m8p7m,4z6m2s5m1z8p$75s39p4z,99m3174z$6z13s1z9s_2m)')
    table.fromEasyStr('(0,1,1,2,5p,240,240,270,240)(12457m24677p468s-3z)(7z1p9m8s2z9p$9s5z5m,9m75z2m2s4z$9s6z3p,9s35z1s11p$6s5m_3s1z,9p343z99m$2p9m333z)')
    table.fromEasyStr('(1,1,1,3,3p,,,,)(1168m35779p2334s-6s,13+,13+,10+10-_213m)(246z9s12z$8s22m6p,32175z3s$5m77s1p,9s62z6p2m8p$_7s9m1p3m,6z61299s$2p9m333z)')
    table.fromEasyStr('(0,0,2,2,2m,,,,)(11146s345p23m-4p10-5_55z)(46z8m979p$6z895m1p9s$8p,217z29s9m$8s7p9s7z1p5m$_4p,23614z7s$1m98s86p4s$_6m,3z9m2s65z1p$2p1z5p7z3p8m$4z)')
    table.fromEasyStr('(1,0,1,1,2s,250,250,201,289)(236789m24678p34s-9m)(3752z1p9s$7s,271z18m1s$7m,1m65z8p26m$_4s,4z9m61z5m5z$2p3z)')
    # table.fromEasyStr('(0,0,2,1,4z,240,250,240,250)()(6_T,6白,6南,+*++*++*+)')
    # 局 本场 立直棒 自家 宝牌 四家得点
    table.fromEasyStr('(6,1,0,3,3z,419,201,75,305)(88m12346s123579p-4s,10+10-5_55z)(1z9s1m9s1p3z$5m9m,8p2m1p3p7m7z$2z4m5p4z,2z1z7z4z3z2s$3m5p5z1s9p,9p1s1m6z9s2p$7z9m2m7m)')
    table.fromEasyStr('(3,2,0,1,5m,224,142,184,450)(11334789m234p67s-1z,13+,13+,10+10-_978p)(6z5z3s3z6z8m$9s5z8p2p,9s1s1s5z4z7z$9p1p2p9p,3z4z5z4s7z2z$6m2s8p`9p,1s3z2z5z8s9s$7z1p5p2m4s)')
    table.fromEasyStr('(4,0,0,0,4m,,,,)(4778m1167p12388s-3m,10+10-55_5z)(4z1m1z9p5z2z$1s5s,1m9p2s6s1z5p$4s3z2m,4z2z9p`5z3z9m$2m6z3s,1z1m9s6z1s1p$5p8p8s)')
    table.fromEasyStr('(0,0,1,0,1m,250,250,240,250)(666m234p56s77z10-_867p)(9p9s5z4z1p2s$1s9m8m2m5z8s$3p1p1z,4z1p1s8p8m9m$6p5z6z8m1s7s$9p2p4s,2z3z9s5z9p1m$1z8p9m3s4s6s$7m6z_2p7z,3z4z7z9m3z1p$6z3s8p1z2z1z$8m2z4s)')
    table.fromEasyStr('(0,0,1,1,5m,210,210,210,360)(23789m466789p44z-5p,13+,10+10-_456p,13+)(1p5z6s1p8s2s$1s9p7z,4z6z3z6s2p1m$7z9m,2z1m9m6z6z9s$7s3z1z5s,2z9s3z8s9p9m$3p4m2m_5s)')
    table.fromEasyStr('(5,2,0,3,9p,462,351,83,104)(23888m56789p666z-6p,7+10-77_7z-_321p,13+,13+)(3z5z1s5z1z5m$2p4s7z,2m6m5s5m9m5z$1s3z6s2z,1p3z2m2m8s4z$2z7p2s1z,4z1z5z1m9m1p$3s4z9m8s)')
    img = table.generateImg()
    img.show()

    outfilepath = r'H:\Life\Project\markdown\mahjong\79博客\assets'
    import os
    outpath = os.path.join(outfilepath, 'table18'+'.png')
    img.save(outpath)

