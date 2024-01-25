import csv
import os
import xml.etree.ElementTree as ET

from tqdm import tqdm

from mahjong_pic.mahjong_series import MahjongSeries
from mahjong_pic.shanten import calc_tenpai, clac_youkouhai, tenhou_to_vector


def int_list(string):
    """
    把一个列表的字符串变成真的列表
    """
    ret = string.split(',')
    ret = [int(it) for it in ret]
    return ret


class Player:
    def __init__(self):
        self.hai = []
        self.tsumo: int | None = None
        self.fuuro = []
        self.kawa = []
        self.riichi = -1  # 表示第n张牌应该横置

        self.junme = 0


def single_hai(hai_num):
    """
    把单张序号牌转化为牌名
    """
    s = 'mpsz'[hai_num // 36]
    n = (hai_num % 36) // 4 + 1
    if n == 5 and hai_num % 4 == 0 and s != 'z':
        n = 0
    return str(n) + s


def to_hai(arr):
    return ''.join([single_hai(it) for it in arr])


def process_fuuro(m: int):
    """
    把天凤的副露代码转换为具体的牌
    @param m: 副露代码
    @return:
        which_index 要从被副露的人那里拿走的手牌
        indexes 从子家手里拿走的牌
        fuuro_str 副露字符串
        fuuro_old_string 加杠时原先的字符串
    """
    from_who = m & 0x0003  # 自家 下家 对家 上家
    if m & 0x0004:  # 顺子
        pattern = (m & 0xFC00) >> 10
        which = pattern % 3  # 吃的牌是三张牌里的第几张
        p = pattern // 3
        suits = 'mps'[p // 7]
        n = p % 7 + 1  # 最小的牌是多少
        numbers = [n, n + 1, n + 2]  # 三张牌分别是什么
        a = ((m & 0x0018) >> 3, (m & 0x0060) >> 5, (m & 0x0180) >> 7)  # 使用的牌是四张牌里的第几张 也就是所谓的牌添字
        index = p // 7 * 36 + (n - 1) * 4
        indexes = [index + a[0], index + 4 + a[1], index + 8 + a[2]]  # 三张牌的序号
        for i in range(3):  # 检查是否是赤牌 是的话修改number
            if numbers[i] == 5 and a[i] == 0:
                numbers[i] = 0  # 0表示赤牌
            break
        which_index = indexes[which]  # 吃来的牌的序号
        indexes.remove(which_index)  # 自己要用掉的牌的序号
        which_number = numbers[which]  # 吃来的牌的数字
        numbers.remove(which_number)  # 自己要用掉的牌的数字
        fuuro_str = f'_{which_number}{numbers[0]}{numbers[1]}{suits}'
        return which_index, indexes, fuuro_str, None
    elif m & 0x0018:  # 刻子 加杠
        pattern = (m & 0xFE00) >> 9
        pon_a = pattern % 3  # 鸣的牌的牌添字（不完全是 见下） 加杠时也是原先下面那张
        p = pattern // 3
        suits = 'mpsz'[p // 9]
        n = p % 9 + 1  # 这些牌的数字是多少
        numbers = [n, n, n, n]  # 自己的两张 碰的一张 加杠的一张
        a = (m & 0x0060) >> 5  # 刻子不包含的牌 或者加杠时加上的牌
        pon_a = pon_a if a > pon_a else pon_a + 1  # 很怪 但是跳过了加杠时那张牌

        if suits != 'z' and n == 5:
            if a == 0:
                numbers[3] = 0  # 赤宝牌是第四张
            elif pon_a == 0:  # 碰了赤宝牌
                numbers[2] = 0
            else:  # 赤宝牌本来就在手里
                numbers[1] = 0
        base_index = p // 9 * 36 + (n - 1) * 4
        if m & 0x0010:  # 加杠
            if from_who == 1:
                fuuro_str = f'{numbers[0]}{numbers[1]}_({numbers[2]}{numbers[3]}){suits}'
                fuuro_old_string = f'{numbers[0]}{numbers[1]}_{numbers[2]}{suits}'
            elif from_who == 2:
                fuuro_str = f'{numbers[0]}_({numbers[2]}{numbers[3]}){numbers[1]}{suits}'
                fuuro_old_string = f'{numbers[0]}_{numbers[2]}{numbers[1]}{suits}'
            elif from_who == 3:
                fuuro_str = f'_({numbers[2]}{numbers[3]}){numbers[0]}{numbers[1]}{suits}'
                fuuro_old_string = f'_{numbers[2]}{numbers[0]}{numbers[1]}{suits}'
            else:
                raise Exception('from_who error')
            # 加杠时 pon_a是原来那张 a才是加杠的那张
            return base_index + a, [], fuuro_str, fuuro_old_string
        else:
            if from_who == 1:
                fuuro_str = f'{numbers[0]}{numbers[1]}_{numbers[2]}{suits}'
            elif from_who == 2:
                fuuro_str = f'{numbers[0]}_{numbers[1]}{numbers[2]}{suits}'
            elif from_who == 3:
                fuuro_str = f'_{numbers[0]}{numbers[1]}{numbers[2]}{suits}'
            else:
                raise Exception('from_who error')
            which_index = base_index + pon_a
            indexes = [base_index, base_index + 1, base_index + 2, base_index + 3]
            indexes.remove(which_index)
            indexes.remove(base_index + a)
            return which_index, indexes, fuuro_str, None
    else:  # 暗杠 大明杠
        pattern = (m & 0xFF00) >> 8
        r = pattern % 4  # 鸣的牌的牌添字
        p = pattern // 4
        suit = 'mpsz'[p // 9]
        n = p % 9 + 1

        base_index = p // 9 * 36 + (n - 1) * 4
        red = suit != 'z' and n == 5
        flag = 0 if r == 0 and red else n  # 鸣的牌是赤宝牌
        flag_me = 0 if r != 0 and red else n
        if from_who == 0:  # 暗杠
            flag = 0 if red else n  # 暗杠了赤宝牌
            fuuro_str = f'+{n}{flag}{suit}+'
            indexes = [base_index, base_index + 1, base_index + 2, base_index + 3]
            return None, indexes, fuuro_str, None
        elif from_who == 1:
            fuuro_str = f'{n}{n}{flag_me}_{flag}{suit}'
        elif from_who == 2:
            fuuro_str = f'{n}_{flag}{n}{flag_me}{suit}'
        else:
            fuuro_str = f'_{flag}{n}{n}{flag_me}{suit}'
        which_index = base_index + r
        indexes = [base_index, base_index + 1, base_index + 2, base_index + 3]
        indexes.remove(which_index)
        return which_index, indexes, fuuro_str, None


def player_hai(player: Player):
    """
    写出玩家的手牌字符串和牌河字符串
    @param player: 玩家
    @return:
    """
    # todo 自摸牌和副露应该分开写
    hai = player.hai
    tsumo = player.tsumo
    fuuro = player.fuuro
    kawa = player.kawa
    riichi = player.riichi
    hai_str = to_hai(hai)
    if tsumo is not None:
        hai_str = hai_str + '-' + single_hai(tsumo)
    if len(fuuro) > 0:
        hai_str = hai_str + '10-' + '-'.join(fuuro[::-1])

    kawa = [single_hai(it) for it in kawa]
    if player.riichi > -1 and len(kawa) > player.riichi:
        kawa[player.riichi] = '_' + kawa[player.riichi]
    for i in range(min((len(kawa) - 1) // 6, 3)):
        kawa[i * 6 + 6] = '$' + kawa[i * 6 + 6]
    return hai_str, ''.join(kawa)


class TenhouTable:
    """
    一个麻将桌 内含解析天凤牌谱并演算下去的功能
    """
    # 视角是以东一局的亲家为自家的 我们接下来称它为主视角
    # 主视角下家对家上家分别记为0123
    kyoku = 0
    oya = 0
    honba = 0
    kyoutaku = 0
    dora_jyouji = []
    tennsu = []
    player = [Player(), Player(), Player(), Player()]

    root = []
    index = 0
    total_index = 0

    callback_before = lambda me, ele: None
    callback_after = lambda me, ele: None

    def load_xml(self, path):
        """
        读取天凤牌谱
        @param path: 牌谱路径
        @return:
        """
        self.root = [element for element in ET.parse(path).getroot()][4:]
        # 舍弃了开头的SHUFFLE GO UN TAIKYOKU
        self.index = 0
        self.total_index = len(self.root)

    def is_over(self):
        return self.index == self.total_index

    def step(self):
        """
        进行一个步骤 也就是天凤牌谱里一个元素
        @return: is_over 对局是否已经结束
        """
        if self.index == len(self.root):
            return True
        element: ET.Element = self.root[self.index]
        self.index += 1

        if element.tag == 'UN':  # 不知道为什么有时会出现这个
            return False

        self.callback_before(element)

        if element.tag == "INIT":
            over_status(self, element)
            kyoku, honba, kyoutaku, _, _, dora_jyouji = int_list(element.attrib['seed'])
            self.kyoku = kyoku
            self.oya = kyoku % 4
            self.honba = honba
            self.kyoutaku = kyoutaku
            self.dora_jyouji = [dora_jyouji]
            self.tennsu = int_list(element.attrib['ten'])
            self.player = [Player(), Player(), Player(), Player()]
            for i in range(4):
                self.player[i].hai = int_list(element.attrib['hai' + str(i)])
                self.player[i].hai.sort()
        elif element.tag == "REACH":
            who = int(element.attrib['who'])
            if element.attrib['step'] == '1':  # 立直宣言
                self.player[who].riichi = len(self.player[who].kawa)
            elif element.attrib['step'] == '2':  # 立直成功
                self.tennsu = int_list(element.attrib['ten'])
                self.kyoutaku += 1
        elif element.tag == "DORA":
            self.dora_jyouji.append(int(element.attrib['hai']))
        elif element.tag == "AGARI":
            pass
        elif element.tag == "RYUUKYOKU":
            pass
        elif element.tag[0] in "TUVW":  # TUVW为摸牌
            player: Player = self.player[ord(element.tag[0]) - ord('T')]
            player.tsumo = int(element.tag[1:])
        elif element.tag[0] in "DEFG":  # DEFG为切牌
            player: Player = self.player[ord(element.tag[0]) - ord('D')]
            player.junme += 1
            hai = int(element.tag[1:])
            player.kawa.append(hai)
            if hai != player.tsumo:
                player.hai.remove(hai)
                if player.tsumo is not None:
                    player.hai.append(player.tsumo)
                player.hai.sort()
            player.tsumo = None
        elif element.tag == "N":
            who = int(element.attrib['who'])  # 表示谁鸣牌了
            m = int(element.attrib['m'])  # 面子编码
            from_who = m & 0x0003  # 表示相对于鸣牌者的哪家
            from_who = (who + from_who) % 4  # 被鸣牌者
            if m & 0x0004 or m & 0x0008 or m & 0x003C == 0 or m & 0x0003 == 0:  # 顺子 刻子 大明杠 自家打的（暗杠）
                which_index, indexes, fuuro_str, _ = process_fuuro(m)
                if which_index is not None:
                    self.player[from_who].kawa.remove(which_index)
                if self.player[who].tsumo is not None:  # 暗杠自摸
                    self.player[who].hai.append(self.player[who].tsumo)
                    self.player[who].tsumo = None
                    self.player[who].hai.sort()
                self.player[who].hai = [x for x in self.player[who].hai if x not in indexes]
                self.player[who].fuuro.append(fuuro_str)
            elif m & 0x0010:  # 加杠
                which_index, _, fuuro_str, fuuro_old_str = process_fuuro(m)
                # 加杠的时候 可能是打出去再加杠（下家有吃的可能） 也可能是直接加杠
                if self.player[who].tsumo == which_index:
                    self.player[who].tsumo = None
                elif which_index in self.player[who].kawa:
                    self.player[who].kawa.remove(which_index)
                else:
                    self.player[who].hai.remove(which_index)
                    self.player[who].hai.append(self.player[who].tsumo)
                    self.player[who].hai.sort()
                self.player[who].fuuro = [fuuro_str if it == fuuro_old_str else it for it in self.player[who].fuuro]

        self.callback_after(element)

        return False

    def generate_img(self):
        info = f'{self.kyoku},{self.honba},{self.kyoutaku},{(4 - self.oya) % 4},{to_hai(self.dora_jyouji)},{self.tennsu[0]},{self.tennsu[1]},{self.tennsu[2]},{self.tennsu[3]}'
        hais = []
        kawas = []
        for i in range(4):
            hai, kawa = player_hai(self.player[i])
            hais.append(hai)
            kawas.append(kawa)
        hai_str = ','.join(hais)
        kawa_str = ','.join(kawas)
        return f'({info})({hai_str})({kawa_str})'


class Tenhou6Table(TenhouTable):
    pass


kyoku_honba = []  # 局数 本场统计量
riichi_tongji = []

riichi_flag = [False, False, False, False]
new_riich = [[], [], [], []]


def over_status(table, element):
    for i in range(4):
        if table.player[i].riichi >= 0:
            riichi_tongji.append(new_riich[i])


def init_status(table, element):
    global riichi_flag
    global new_riich
    kyoku_honba.append((table.kyoku, table.honba))
    riichi_flag = [False, False, False, False]
    new_riich = [[], [], [], []]


def reach_status(table, element):
    global riichi_flag
    global new_riich
    who = int(element.attrib['who'])
    if element.attrib['step'] == '1':
        riichi_flag[who] = True
        new_riich[who].append(who)
    if element.attrib['step'] == '2':
        pass


def fuuro_status(table, element):
    pass


def agari_status(table, element):
    global riichi_flag
    global new_riich
    who = int(element.attrib['who'])
    if table.player[who].riichi >= 0:
        new_riich[who].append(int(element.attrib['ten'].split(',')[1]))
    if 'owari' in element.attrib:
        over_status(table, element)


def ryuukyoku_statue(table, element):
    global riichi_flag
    global new_riich
    for i in range(4):
        if new_riich[i] != []:
            new_riich[i].append(0)
    if 'owari' in element.attrib:
        over_status(table, element)


def defg_status(table, element):
    global riichi_flag
    global new_riich
    who = ord(element.tag[0]) - ord('D')
    if riichi_flag[who]:
        riichi_flag[who] = False
        player = table.player[who]
        new_riich[who].append(table.kyoku)
        new_riich[who].append(table.honba)
        new_riich[who].append(player.junme)
        new_riich[who].append(table.player[table.oya].junme)
        new_riich[who].append(sum([it.junme for it in table.player]))
        new_riich[who].append(int(element.tag[1:]))
        new_riich[who].append(table.tennsu[who])
        hai = player.hai
        m = MahjongSeries()
        m.from_tenhou0(hai)
        new_riich[who].append(clac_youkouhai(tenhou_to_vector(m.to_tenhou()))[0])
        pass


def tuvw_status(table, element):
    pass


kyoku_honba_tongji = []

if __name__ == '__main__':
    table = TenhouTable()

if __name__ == '__main__':

    table = TenhouTable()

    dirs = os.listdir('./paipu/2022scc/')
    for dir in dirs:
        paths = os.listdir(f'./paipu/2022scc/{dir}')
        for path in paths:
            path = f'./paipu/2022scc/{dir}/{path}'
            table.load_xml(path)
            while not table.is_over():
                table.step()
            kyoku_honba_tongji.append((kyoku_honba[-1][0], len(kyoku_honba)))
            kyoku_honba = []

        with open(f'./paipu/2022csv/{dir}_riichi.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(riichi_tongji)

        with open(f'./paipu/2022csv/{dir}.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(kyoku_honba_tongji)

        riichi_tongji = []
        kyoku_honba_tongji = []

    # 巡目 听牌数 打哪张立直 立直通过率 被破一发率 和率 自摸率 立直时点数 追立率 和牌点数
    # 庄家立直率 平均立直数
    # 总巡数

    # 先写个简单的
    # 总巡数 总局数 平均本场数

    # 立直的平均面听数 平均巡目 和率 立直时分数
