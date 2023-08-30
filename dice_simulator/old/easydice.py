import random

import numpy as np
from tqdm import tqdm

class Cha:
    def __init__(self, atk, hp, ap):
        self.atk = atk
        self.hp = hp
        self.ap = ap

    def dice(self):
        return random.randint(1, 100) + self.atk + int(np.ceil(self.ap//20))

    def hurt(self, atk):
        if self.ap > 0:
            self.ap -= atk
            if self.ap < 0:
                self.ap = 0
        else:
            self.hp -= 1

    def check(self):
        return self.hp <= 0

def fight(cha1:Cha, cha2:Cha):
    while True:
        d1 = cha1.dice()
        d2 = cha2.dice()
        if (d1==d2):
            continue
        if d1>d2:
            cha2.hurt(d1)
            if cha2.check():
                return 1
        else:
            cha1.hurt(d2)
            if cha1.check():
                return 0

win = 0
for i in tqdm(range(1000000)):
    nana = Cha(85, 3, 0)
    luna = Cha(61, 1, 220)
    win += fight(nana, luna)

print(win / 10000, '%')

