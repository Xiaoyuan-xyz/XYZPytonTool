# 解析牌谱

# ! 一局对战的格式
# 以https://tenhou.net/0/log/?2022010117gm-00a9-0000-f9ccdd15
# 南二局 零本场为例

# tenhou格式
tenhou = '<INIT seed="5,0,0,5,5,110" ten="383,181,2,434" oya="1" hai0="79,47,29,15,94,98,37,38,58,109,50,87,128" hai1="105,81,72,55,65,107,77,120,100,16,121,104,11" hai2="25,75,70,46,115,41,32,44,74,22,42,119,0" hai3="49,1,116,64,118,12,4,132,26,103,19,9,84"/><U125/><E65/><V68/><F119/><N who="3" m="45611" /><G132/><T53/><D128/><U93/><E55/><V113/><F0/><W34/><G103/><T28/><D109/><U20/><E11/><V80/><F80/><W6/><G64/><T69/><D69/><N who="2" m="26730" /><F22/><W14/><G1/><T108/><D108/><U127/><E16/><V111/><F32/><W135/><G135/><T45/><D37/><U92/><E20/><V123/><F25/><W67/><G67/><T117/><D38/><U18/><E18/><V97/><F97/><W59/><G84/><T129/><D129/><U131/><E131/><V61/><F111/><W5/><G59/><T2/><D2/><U13/><E13/><V86/><F86/><W88/><G49/><T63/><D15/><U83/><E81/><V96/><F96/><W30/><G12/><T122/><D45/><N who="2" m="17514" /><F61/><W62/><G62/><T33/><D117/><U78/><E78/><V73/><F123/><N who="1" m="47177" /><E100/><V48/><F48/><W40/><G19/><T24/><D122/><U8/><E8/><V102/><F102/><W17/><G17/><T112/><D28/><U31/><E31/><V7/><F7/><W52/><G14/><T66/><D79/><U114/><E93/><V36/><F36/><W10/><G9/><T51/><D51/><U90/><E92/><V130/><F130/><W82/><G10/><T3/><D3/><U85/><E77/><V126/><F126/><N who="1" m="48137" /><E72/><N who="2" m="18435" /><V60/><DORA hai="124" /><F60/><W27/><G30/><T133/><D29/><U43/><E43/><AGARI ba="0,0" hai="41,42,43,113,115" m="18435,17514,26730" machi="43" ten="50,8000,1" yaku="28,2,52,2" doraHai="110,124" who="2" fromWho="1" sc="383,0,181,-80,2,80,434,0" />'

# tenhou6格式
tenhou6 = {"title": ["", ""], "name": ["Aさん", "Bさん", "Cさん", "Dさん"], "rule": {"aka": 1}, "log": [
    [[5, 0, 0], [38300, 18100, 200, 43400], [41, 45], [],
     [14, 18, 21, 21, 23, 24, 26, 32, 34, 36, 37, 41, 46],
     [25, 18, 29, 41, 23, 43, 46, 11, 27, 44, 19, 17, 42, 28, 24, 11, 47],
     [46, 41, 60, 60, 21, 21, 60, 60, 14, 23, 43, 44, 18, 32, 60, 60, 18],
     [13, 51, 25, 28, 31, 32, 33, 38, 39, 39, 39, 44, 44],
     [45, 36, 16, 45, 36, 15, 46, 14, 33, 32, "4444p44", 13, 18, 42, 35, 34, "4545p45", 22],
     [28, 25, 13, 51, 16, 60, 60, 60, 33, 60, 38, 60, 60, 36, 36, 32, 31, 60],
     [11, 16, 17, 19, 22, 22, 23, 23, 29, 31, 31, 42, 43],
     [29, 42, 33, "29p2929", 41, 44, 37, 27, 34, 37, "23p2323", 31, 24, 38, 12, 21, 46, 45, "m31313131", 27],
     [43, 11, 60, 16, 19, 17, 60, 41, 60, 60, 27, 44, 60, 60, 60, 60, 60, 60, 0, 60],
     [11, 12, 13, 14, 15, 17, 24, 28, 34, 38, 43, 43, 47],
     ["p434343", 19, 12, 14, 47, 28, 26, 12, 53, 18, 27, 22, 15, 52, 13, 33, 17],
     [47, 38, 28, 11, 60, 60, 34, 26, 24, 14, 60, 15, 60, 14, 13, 13, 18],
     ["和了", [0, -8000, 8000, 0], [2, 1, 2, "満貫8000点", "対々和(2飜)", "ドラ(2飜)"]]]]}

# koba格式
# https://kobalab.net/majiang/paipu.html?tenhou-log/2022010117gm-00a9-0000-f9ccdd15.json#/0/7/0:i
null = None
koba = [{"qipai": {"zhuangfeng": 1, "jushu": 1, "changbang": 0, "lizhibang": 0, "defen": [18100, 200, 43400, 38300],
                   "baopai": "z1",
                   "shoupai": ["m30p58s1238999z44", "m1679p22339s11z23", "m123457p48s48z337", "m48p11346s2467z16"]}},
        {"zimo": {"l": 0, "p": "z5"}}, {"dapai": {"l": 0, "p": "p8"}}, {"zimo": {"l": 1, "p": "p9"}},
        {"dapai": {"l": 1, "p": "z3"}}, {"fulou": {"l": 2, "m": "z333-"}}, {"dapai": {"l": 2, "p": "z7"}},
        {"zimo": {"l": 3, "p": "p5"}}, {"dapai": {"l": 3, "p": "z6"}}, {"zimo": {"l": 0, "p": "s6"}},
        {"dapai": {"l": 0, "p": "p5"}}, {"zimo": {"l": 1, "p": "z2"}}, {"dapai": {"l": 1, "p": "m1"}},
        {"zimo": {"l": 2, "p": "m9"}}, {"dapai": {"l": 2, "p": "s8"}}, {"zimo": {"l": 3, "p": "m8"}},
        {"dapai": {"l": 3, "p": "z1"}}, {"zimo": {"l": 0, "p": "m6"}}, {"dapai": {"l": 0, "p": "m3"}},
        {"zimo": {"l": 1, "p": "s3"}}, {"dapai": {"l": 1, "p": "s3_"}}, {"zimo": {"l": 2, "p": "m2"}},
        {"dapai": {"l": 2, "p": "p8"}}, {"zimo": {"l": 3, "p": "p9"}}, {"dapai": {"l": 3, "p": "p9_"}},
        {"fulou": {"l": 1, "m": "p999="}}, {"dapai": {"l": 1, "p": "m6"}}, {"zimo": {"l": 2, "p": "m4"}},
        {"dapai": {"l": 2, "p": "m1"}}, {"zimo": {"l": 3, "p": "z1"}}, {"dapai": {"l": 3, "p": "z1_"}},
        {"zimo": {"l": 0, "p": "z5"}}, {"dapai": {"l": 0, "p": "m0"}}, {"zimo": {"l": 1, "p": "z1"}},
        {"dapai": {"l": 1, "p": "m9"}}, {"zimo": {"l": 2, "p": "z7"}}, {"dapai": {"l": 2, "p": "z7_"}},
        {"zimo": {"l": 3, "p": "p3"}}, {"dapai": {"l": 3, "p": "p1"}}, {"zimo": {"l": 0, "p": "s6"}},
        {"dapai": {"l": 0, "p": "m6"}}, {"zimo": {"l": 1, "p": "z4"}}, {"dapai": {"l": 1, "p": "m7"}},
        {"zimo": {"l": 2, "p": "p8"}}, {"dapai": {"l": 2, "p": "p8_"}}, {"zimo": {"l": 3, "p": "z3"}},
        {"dapai": {"l": 3, "p": "p1"}}, {"zimo": {"l": 0, "p": "m5"}}, {"dapai": {"l": 0, "p": "m5_"}},
        {"zimo": {"l": 1, "p": "s7"}}, {"dapai": {"l": 1, "p": "s7_"}}, {"zimo": {"l": 2, "p": "p6"}},
        {"dapai": {"l": 2, "p": "s4"}}, {"zimo": {"l": 3, "p": "z6"}}, {"dapai": {"l": 3, "p": "z6_"}},
        {"zimo": {"l": 0, "p": "z6"}}, {"dapai": {"l": 0, "p": "z6_"}}, {"zimo": {"l": 1, "p": "p7"}},
        {"dapai": {"l": 1, "p": "z1"}}, {"zimo": {"l": 2, "p": "m2"}}, {"dapai": {"l": 2, "p": "p6"}},
        {"zimo": {"l": 3, "p": "m1"}}, {"dapai": {"l": 3, "p": "m1_"}}, {"zimo": {"l": 0, "p": "m4"}},
        {"dapai": {"l": 0, "p": "m4_"}}, {"zimo": {"l": 1, "p": "s4"}}, {"dapai": {"l": 1, "p": "s4_"}},
        {"zimo": {"l": 2, "p": "s0"}}, {"dapai": {"l": 2, "p": "p4"}}, {"zimo": {"l": 3, "p": "p7"}},
        {"dapai": {"l": 3, "p": "m4"}}, {"zimo": {"l": 0, "p": "s3"}}, {"dapai": {"l": 0, "p": "s3"}},
        {"zimo": {"l": 1, "p": "s7"}}, {"dapai": {"l": 1, "p": "s7_"}}, {"zimo": {"l": 2, "p": "m8"}},
        {"dapai": {"l": 2, "p": "m4"}}, {"zimo": {"l": 3, "p": "z4"}}, {"dapai": {"l": 3, "p": "p3"}},
        {"fulou": {"l": 1, "m": "p333="}}, {"dapai": {"l": 1, "p": "p7"}}, {"zimo": {"l": 2, "p": "p7"}},
        {"dapai": {"l": 2, "p": "p7_"}}, {"zimo": {"l": 3, "p": "m9"}}, {"dapai": {"l": 3, "p": "z3"}},
        {"zimo": {"l": 0, "p": "s2"}}, {"dapai": {"l": 0, "p": "s2_"}}, {"zimo": {"l": 1, "p": "s1"}},
        {"dapai": {"l": 1, "p": "z4"}}, {"fulou": {"l": 0, "m": "z444+"}}, {"dapai": {"l": 0, "p": "s8"}},
        {"zimo": {"l": 1, "p": "p4"}}, {"dapai": {"l": 1, "p": "p4_"}}, {"zimo": {"l": 2, "p": "p2"}},
        {"dapai": {"l": 2, "p": "m5"}}, {"zimo": {"l": 3, "p": "m7"}}, {"dapai": {"l": 3, "p": "z4"}},
        {"zimo": {"l": 0, "p": "m3"}}, {"dapai": {"l": 0, "p": "m3_"}}, {"zimo": {"l": 1, "p": "s8"}},
        {"dapai": {"l": 1, "p": "s8_"}}, {"zimo": {"l": 2, "p": "m5"}}, {"dapai": {"l": 2, "p": "m5_"}},
        {"zimo": {"l": 3, "p": "z2"}}, {"dapai": {"l": 3, "p": "m8"}}, {"zimo": {"l": 0, "p": "m8"}},
        {"dapai": {"l": 0, "p": "m8_"}}, {"zimo": {"l": 1, "p": "m2"}}, {"dapai": {"l": 1, "p": "m2_"}},
        {"zimo": {"l": 2, "p": "p0"}}, {"dapai": {"l": 2, "p": "m4"}}, {"zimo": {"l": 3, "p": "p8"}},
        {"dapai": {"l": 3, "p": "s2"}}, {"zimo": {"l": 0, "p": "z2"}}, {"dapai": {"l": 0, "p": "s6"}},
        {"zimo": {"l": 1, "p": "p1"}}, {"dapai": {"l": 1, "p": "p1_"}}, {"zimo": {"l": 2, "p": "m3"}},
        {"dapai": {"l": 2, "p": "m3"}}, {"zimo": {"l": 3, "p": "p4"}}, {"dapai": {"l": 3, "p": "p4_"}},
        {"zimo": {"l": 0, "p": "s5"}}, {"dapai": {"l": 0, "p": "s6"}}, {"zimo": {"l": 1, "p": "z6"}},
        {"dapai": {"l": 1, "p": "z6_"}}, {"zimo": {"l": 2, "p": "s3"}}, {"dapai": {"l": 2, "p": "m3"}},
        {"zimo": {"l": 3, "p": "m1"}}, {"dapai": {"l": 3, "p": "m1_"}}, {"zimo": {"l": 0, "p": "s4"}},
        {"dapai": {"l": 0, "p": "s2"}}, {"zimo": {"l": 1, "p": "z5"}}, {"dapai": {"l": 1, "p": "z5_"}},
        {"fulou": {"l": 0, "m": "z555+"}}, {"dapai": {"l": 0, "p": "s1"}}, {"fulou": {"l": 1, "m": "s1111-"}},
        {"gangzimo": {"l": 1, "p": "p7"}}, {"dapai": {"l": 1, "p": "p7_"}}, {"kaigang": {"baopai": "z5"}},
        {"zimo": {"l": 2, "p": "m7"}}, {"dapai": {"l": 2, "p": "m8"}}, {"zimo": {"l": 3, "p": "z7"}},
        {"dapai": {"l": 3, "p": "m8"}}, {"zimo": {"l": 0, "p": "p2"}}, {"dapai": {"l": 0, "p": "p2_"}}, {
            "hule": {"l": 1, "shoupai": "p22z22p2,p999=,p333=,s1111-", "baojia": 0, "fubaopai": null, "defen": 8000,
                     "hupai": [{"name": "対々和", "fanshu": 2}, {"name": "ドラ", "fanshu": 2}],
                     "fenpei": [-8000, 8000, 0, 0], "fu": 50, "fanshu": 4}}]

# 我自己的格式


# ! 牌局总信息

# tenhou格式
tenhou_all = f'''<mjloggm ver="2.3">
    <SHUFFLE seed="{'此处略去随机数种子'}" ref=""/>
    <GO type="169" lobby="0"/>
    <UN n0="%E9%9B%B7%E8%94%B5" n1="%E8%88%B9%E8%A6%8B%E7%B5%90%E8%A1%A3" n2="%52%35" n3="%E7%9B%9B%E5%B2%A1%E3%81%AE%E3%83%AA%E3%83%BC%E3%83%81%E8%B6%85%E4%BA%BA" dan="16,17,16,17" rate="2073.88,2181.97,2195.75,2192.05" sx="M,F,M,M"/>
    <TAIKYOKU oya="0"/>
    {'在这里并列地填入局信息'}
</mjloggm>
'''

# koba格式
koba_all = {"title": "四鳳南喰赤\n2022010117gm-00a9-0000-f9ccdd15",
    "player": ["雷蔵\n(七段 R2073)", "船見結衣\n(八段 R2181)", "R5\n(七段 R2195)", "盛岡のリーチ超人\n(八段 R2192)"],
    "qijia": 0, "log": [# ?在此处填入每一局的信息
    ], "defen": [30000, 12800, 19500, 37700], "point": ["10.0", "-37.0", "-20.0", "47.0"], "rank": [2, 4, 3, 1]}

# 我自己的格式

# ! 手牌格式

mahjong = '22p22z-7p10-_1111s-3_33p-9_99p'
# https://blog.kobalab.net/entry/20151211/1449838875
mahjong_koba = 'p22z22p7,p999=,p333=,s1111-'

# 更丰富的表示格式
# https://blog.kobalab.net/entry/20161218/1482078427
mahjong_text_koba = '{s067z1 z1}(ツモ) {p2-13} {z66=6-6} {_z77_} {  }(ドラ){m1}'
mahjong_text = '067s1z---[ツモ]-1z10-_213p-6^66z-+77z+---[ドラ]-1m'

# 门前手牌格式
mahjong1 = '22p222z'
vec = []
arr = []


# 副露格式
fulu_tenhou = 53399
fulu_koba = 's40-6'
fulu = '4_06s'


