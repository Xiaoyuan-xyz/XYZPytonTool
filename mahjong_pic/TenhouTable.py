import xml.etree.ElementTree as ET
import tkinter as tk
from MahjongTable import MahjongTable
from  PIL import ImageTk



def int_list(string):
    ret = string.split(',')
    ret = [int(it) for it in ret]
    return ret


class Player:
    hai = []
    tsumo:int = None
    fuuro = []
    kawa = []
    riichi = -1   # 表示第n张牌应该横置

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

def process_fuuro(m:int):
    from_who = m & 0x0003 # 自家 下家 对家 上家
    if m & 0x0004: # 顺子
        pattern = (m & 0xFC00) >> 10
        which = pattern % 3  # 吃的牌是第几张
        p = pattern //3
        suits = 'mps'[p//7]
        n = p % 7 + 1  # 最小的牌是多少
        numbers = [n, n+1, n+2] # 三张牌分别是什么
        a = ((m&0x0018)>>3, (m&0x0060)>>5, (m&0x0180)>>7)# 使用的牌是四张牌里的第几张
        index = p//7*36+(n-1)*4
        indexes = [index+a[0], index+4+a[1], index+8+a[2]] # 三张牌的序号
        for i in range(3): # 检查是否是赤牌 是的话修改number
            if numbers[i] == 5 and a[i]==0:
                numbers[i] = 0 # 0表示赤牌
            break
        which_index = indexes[which] # 吃来的牌的序号
        indexes.remove(which_index) # 剩余的牌的序号
        which_number = numbers[which] # 吃来的牌的数字
        numbers.remove(which_number) # 剩余的牌的数字
        fuuro_str = f'_{which_number}{numbers[0]}{numbers[1]}{suits}'
        return from_who, which_index, indexes, fuuro_str, m
    elif m&0x0018: # 刻子 大明杠
        pattern = (m & 0xFE00) >> 9
        which = pattern % 3 # 鸣的牌是第几张
        p = pattern // 3
        suits = 'mpsz'[p // 9]
        n = p % 9 + 1  # 这些牌的数字是多少
        # todo 加杠实现不了














    return '_555p'


def player_hai(player:Player):
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
        kawa[player.riichi] = '_'+kawa[player.riichi]
    for i in range(min((len(kawa)-1)//6,3)):
        kawa[i*6+6] = '$' + kawa[i*6+6]
    return hai_str, ''.join(kawa)




class TenhouTable:
    # 视角是以东一局的亲家为自家的
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

    def load_xml(self, path):
        self.root = [element for element in ET.parse(path).getroot()][4:]
        # 舍弃了开头的SHUFFLE GO UN TAIKYOKU
        self.index = 0
        self.total_index = len(self.root)

    def step(self):
        if self.index == len(self.root):
            return True
        element: ET.Element = self.root[self.index]
        self.index += 1

        print(element.tag)

        if element.tag == "INIT":
            seed = int_list(element.attrib['seed'])
            kyoku, honba, kyoutaku, _, _, dora_jyouji = seed
            self.kyoku = kyoku
            self.oya = kyoku % 4
            self.honba = honba
            self.kyoutaku = kyoutaku
            self.dora_jyouji = [dora_jyouji]
            self.tennsu = int_list(element.attrib['ten'])
            for i in range(4):
                self.player[i].hai = int_list(element.attrib['hai' + str(i)])
                self.player[i].hai.sort()
                self.player[i].fuuro = []
                self.player[i].kawa = []
                self.player[i].riichi = -1
                self.player[i].tsumo = None
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
        elif element.tag == "N":
            pass
        elif element.tag[0] in "TUVW":
            player:Player = self.player[ord(element.tag[0]) - ord('T')]
            player.tsumo = int(element.tag[1:])
        elif element.tag[0] in "DEFG":
            player:Player = self.player[ord(element.tag[0]) - ord('D')]
            hai = int(element.tag[1:])
            player.kawa.append(hai)
            if hai != player.tsumo:
                player.hai.remove(hai)
                player.hai.append(player.tsumo)
                player.hai.sort()
            player.tsumo = None
        return False

    def generate_img(self):
        info = f'{self.kyoku},{self.honba},{self.kyoutaku},{(4-self.oya)%4},{to_hai(self.dora_jyouji)},{self.tennsu[0]},{self.tennsu[1]},{self.tennsu[2]},{self.tennsu[3]}'
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



table = TenhouTable()
table.load_xml("./paipu/2022scc/scc20220101/2022010117gm-00a9-0000-f9ccdd15.xml")
img_table = MahjongTable()

root = tk.Tk()
root.title("Mahjong")
root.geometry("900x800")
label = tk.Label(root) # 麻将桌画在标签上
label.pack()

img_index = -1
img_strs = []

def change_img(*arg):
    global img_index, img_strs, label
    if arg[0].delta < 0: # 向下
        if img_index == len(img_strs) - 1:
            if table.step():
                return
            img_strs.append(table.generate_img())
        img_index += 1
    else:
        if img_index <= 0:
            return
        img_index -= 1

    img_table.fromEasyStr(img_strs[img_index])
    img = img_table.generateImg()
    img = img.resize((800, 800))
    photo = ImageTk.PhotoImage(img)
    label.configure(image=photo)
    label.image = photo


button = tk.Button(root, text='下一张', command=change_img)
button.place(x=0,y=0)
root.bind_all("<MouseWheel>", change_img)


root.mainloop()