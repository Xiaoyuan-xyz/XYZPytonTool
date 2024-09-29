import random
from tqdm import tqdm

class Player:
    name:str
    hp:int
    atk:int
    over:bool

    def __init__(self, name:str, hp:int, atk:int):
        self.name = name
        self.hp = hp
        self.atk = atk
        self.over = False

    def dice(self):
        return random.randint(1, 100) + self.atk

    def attack(self, enemy:'Player'):
        enemy.hp -= 1
        if enemy.hp <= 0:
            enemy.over = True
            return True
        return False


if __name__ == '__main__':
    win = {0: 0, 1: 0, -1:0}
    terra_lost = 0
    for i in tqdm(range(1000000)):
        marisa = Player('魔理沙', 3, 85)
        patchouli = Player('帕秋莉', 2, 120)

        terra = 65
        while not marisa.over and not patchouli.over:
            marisa_dice = marisa.dice()
            patchouli_dice = patchouli.dice()
            # print(f'{marisa.name}掷骰子: {marisa_dice}, {patchouli.name}掷骰子: {patchouli_dice}')
            if marisa_dice > patchouli_dice:
                # print(marisa.name, '攻击', patchouli.name)
                marisa.attack(patchouli)
            elif patchouli_dice > marisa_dice:
                # print(patchouli.name, '攻击', marisa.name)
                patchouli.attack(marisa)
                terra -= patchouli_dice * random.randint(11, 20) / 100
                # print('terra.hp=', terra)
                if terra <= 0:
                    terra_lost += 1
                    if random.randint(1, 100) > 80:
                        # print('同归于尽')
                        marisa.over = True
                        patchouli.over = True
                        break
                    else:
                        # print('魔理沙满身疮痍')
                        marisa.over = True
            else:
                # print('平局')
                pass

        # print(marisa.over - patchouli.over)
        win[marisa.over - patchouli.over] += 1
    print(terra_lost)
    print(win)