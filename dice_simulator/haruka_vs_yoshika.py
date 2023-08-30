import logging
import random

import tqdm


class Message:
    def __init__(self, kind, value=0, skill=None):
        self.kind = kind
        self.value = value
        self.skill: Skill = skill


class Skill:
    def __init__(self, name, level, apply_func):
        self.name = name  # 技能名
        self.level = level  # 妖力值
        self.apply_func = apply_func  # 主动技能释放
        self.owner: Character = None  # 使用者

    def apply(self):
        self.apply_func(self)


class Passive:
    def __init__(self, name, duration, process_func):
        self.name = name  # 技能名
        self.duration = duration  # 持续时间
        self.process_func = process_func  # 被动技能触发
        self.owner: Character = None  # 使用者
        self.is_expired = False  # 已失效

    def process(self, message: Message):
        self.process_func(self, message)


class Character:
    def __init__(self, name, level, hp):
        self.name = name
        self.level = level
        self.hp = hp
        self.max_hp = hp
        self.skills: list[Skill] = []
        self.passives: list[Passive] = []

        self.opponent: Character = None
        self.game: Game = None
        self.history = []
        self.turn = 0
        self.is_dead = False

    def process_message(self, message: Message):
        for passive in self.passives:
            passive.process(message)
        if message.kind == 'ATTACK':
            message.kind = 'HURT'
            self.opponent.process_message(message)
        elif message.kind == 'HEALING':
            self.hp += message.value
            if self.hp > self.max_hp:
                self.hp = self.max_hp
            logging.info(f'{self.name}回复血量 {message.value}  现在血量 {self.hp}')
        elif message.kind == 'HURT':
            message.kind = 'DAMAGE'
            self.process_message(message)
        elif message.kind == 'DAMAGE':
            self.hp -= message.value
            logging.info(f'{self.name}受到伤害 {message.value} 现在血量 {self.hp}')
            if self.hp <= 0:
                self.is_dead = True

    def turn_stage(self):
        self.turn = self.game.turn
        for passive in self.passives:
            passive.duration -= 1
            if passive.duration == 0:
                passive.is_expired = True
        self.passives = [it for it in self.passives if not it.is_expired]

    def skill_stage(self):
        dice = random.randint(1, 6)
        logging.info(f'{self.name} 发动技能{dice} {self.skills[dice - 1].name}')
        self.history.append(dice)
        self.skills[dice - 1].apply()


class Game:
    def __init__(self, cha1: Character, cha2: Character):
        self.cha1 = cha1
        self.cha2 = cha2
        self.cha1.opponent = cha2
        self.cha2.opponent = cha1
        self.cha1.game = self
        self.cha2.game = self
        for skill in self.cha1.skills:
            skill.owner = self.cha1
        for skill in self.cha2.skills:
            skill.owner = self.cha2
        for passive in self.cha1.passives:
            passive.owner = self.cha1
        for passive in self.cha2.passives:
            passive.owner = self.cha2
        self.turn = 0
        self.winner = ''

    def check_over(self):
        if self.cha1.is_dead and not self.cha2.is_dead:
            self.winner = self.cha2.name
        if not self.cha1.is_dead and self.cha2.is_dead:
            self.winner = self.cha1.name
        if self.cha1.is_dead and self.cha2.is_dead:
            self.winner = '两败俱伤'

    def start(self):
        while not self.cha1.is_dead and not self.cha2.is_dead:
            self.turn += 1
            logging.info(f'====== 第{self.turn}回合 ======')
            self.cha1.turn_stage()
            self.cha2.turn_stage()
            if random.randint(1, 2) > 1:
                attacker1 = self.cha1
                attacker2 = self.cha2
            else:
                attacker1 = self.cha2
                attacker2 = self.cha1
            attacker1.skill_stage()
            self.check_over()
            if self.winner != '':
                return
            attacker2.skill_stage()
            self.check_over()
            if self.winner != '':
                return
            # 显示对战双方的血量
            logging.info(f'{self.cha1.name} 血量 {self.cha1.hp}/{self.cha1.max_hp} '
                         f'{self.cha2.name} 血量 {self.cha2.hp}/{self.cha2.max_hp}')

# ! ==========================================================================

debug_mode = False
if debug_mode:
    logging.basicConfig(level=logging.DEBUG)
    n_times = 1
else:
    logging.basicConfig(level=logging.WARN)
    n_times = 100000
result = {'晴夏': 0, '芳香': 0, '两败俱伤': 0}
for i in tqdm.tqdm(range(n_times)):
    def skill_hrk_1(skill: Skill):
        """
        对对方造成1d4点伤害
        """
        dice = random.randint(1, 4)
        message = Message('ATTACK', dice)
        logging.info(f'{skill.name} 发动 造成 {dice} 点伤害')
        skill.owner.process_message(message)


    skill_hrk1 = Skill('小天狗之拳', 1, skill_hrk_1)


    def skill_hrk_2(skill: Skill):
        """
        1d4 4时下回合受到伤害时受伤为0 其他受伤-2
        """
        dice = random.randint(1, 4)
        if dice == 4:
            logging.info(f'{skill.name} 出目{dice} 下回合伤害归零')

            def skill_hrk_2_passive_1(passive: Passive, message: Message):
                if message.kind == 'HURT' and passive.duration == 1:
                    message.value = 0
                    logging.info(f'{skill.name} 发动 伤害归零')

            passive = Passive('抱头蹲防passive1', 2, skill_hrk_2_passive_1)
        else:
            logging.info(f'{skill.name} 出目{dice} 下回合伤害-2')

            def skill_hrk_2_passive_2(passive: Passive, message: Message):
                if message.kind == 'HURT' and passive.duration == 1:
                    message.value -= 2
                    if message.value < 0:
                        message.value = 0
                    logging.info(f'{skill.name} 发动 伤害-2')

            passive = Passive('抱头蹲防passive2', 2, skill_hrk_2_passive_2)
        passive.owner = skill.owner
        skill.owner.passives.append(passive)


    skill_hrk2 = Skill('抱头蹲防', 2, skill_hrk_2)


    def skill_hrk_3(skill: Skill):
        """
        造成1+1d4次1点伤害
        """
        dice = random.randint(2, 5)
        logging.info(f'{skill.name} 发动 造成 {dice} 次伤害')
        for it in range(dice):
            message = Message('ATTACK', 1)
            skill.owner.process_message(message)


    skill_hrk3 = Skill('疯狂乱抓2023', 3, skill_hrk_3)


    def skill_hrk_4(skill: Skill):
        """
        造成5点伤害 1d6>1 则也对自己造成5点伤害
        """
        message = Message('ATTACK', 5)
        logging.info(f'{skill.name} 发动 造成 5 点伤害')
        skill.owner.process_message(message)
        dice = random.randint(1, 6)
        if dice > 1:
            message = Message('HURT', 5)
            logging.info(f'自己受到 5 点伤害')
            skill.owner.process_message(message)


    skill_hrk4 = Skill('舍身冲撞', 4, skill_hrk_4)


    def skill_hrk_5(skill: Skill):
        """
        模仿并使用对方上一张使用的卡牌 如果对方卡牌的妖力值大于等于5 则有妖力值*0.1的概率模仿失败
        如果对方未使用任何卡牌 则模仿失败
        """
        if len(skill.owner.opponent.history) == 0:
            return
        opponent = skill.owner.opponent
        opponent_index = opponent.history[-1]
        opponent_skill = opponent.skills[opponent_index - 1]
        if opponent_skill.level >= 5:
            dice = random.randint(1, 10)
            if dice <= opponent_skill.level:
                logging.info(f'复制技能{opponent_skill.name}失败：{dice}/{opponent_skill.level}')
                return
        logging.info(f'复制了技能 {opponent_skill.name}')
        new_skill = Skill('拷贝技能', opponent_skill.level, opponent_skill.apply_func)
        new_skill.owner = skill.owner
        new_skill.apply()


    skill_hrk5 = Skill('模仿', 5, skill_hrk_5)


    def skill_hrk_6(skill: Skill):
        """
        获得被动技能 涌现 持续1回合 造成伤害与恢复+1
        额外再抽一张牌
        """

        def skill_hrk_6_passive_1(passive: Passive, message: Message):
            if message.kind == 'ATTACK' or message.kind == 'HEALING':
                message.value += 1
                logging.info(f'{skill.name} {passive.name}发动 {message.kind}+1')

        passive = Passive('灵感passive1涌现', 1, skill_hrk_6_passive_1)
        passive.owner = skill.owner
        skill.owner.passives.append(passive)
        skill.owner.skill_stage()


    skill_hrk6 = Skill('灵感', 6, skill_hrk_6)


    def skill_ysk_1(skill: Skill):
        """
        对对方造成1d6点伤害
        """
        dice = random.randint(1, 6)
        message = Message('ATTACK', dice)
        logging.info(f'{skill.name} 发动 造成 {dice} 点伤害')
        skill.owner.process_message(message)


    skill_ysk1 = Skill('毒爪「剧毒抹削」', 1, skill_ysk_1)


    def skill_ysk_2(skill: Skill):
        """
        回复1d4点生命
        """
        dice = random.randint(1, 4)
        message = Message('HEALING', dice)
        logging.info(f'{skill.name} 发动 回复 {dice} 点生命')
        skill.owner.process_message(message)


    skill_ysk2 = Skill('回复「借由欲望的恢复」', 2, skill_ysk_2)


    def skill_ysk_3(skill: Skill):
        """
        造成1点伤害 使对方获得脆弱：受到伤害+1
        """

        message = Message('ATTACK', 1)
        logging.info(f'{skill.name} 发动 造成 1 点伤害 给对方施加脆弱')
        skill.owner.process_message(message)

        def skill_ysk3_passive_1(passive: Passive, message: Message):
            if message.kind == 'HURT':
                message.value += 1
                logging.info(f'{skill.name} {passive.name}发动 {message.kind}+1')

        passive = Passive('毒爪passive1脆弱', 999, skill_ysk3_passive_1)
        passive.owner = skill.owner.opponent
        skill.owner.opponent.passives.append(passive)


    skill_ysk3 = Skill('毒爪「剧毒杀害」', 3, skill_ysk_3)


    def skill_ysk_4(skill: Skill):
        """
        造成3点伤害 1d6>4 再造成2点伤害
        """
        message = Message('ATTACK', 3)
        logging.info(f'{skill.name} 发动 造成 3 点伤害')
        skill.owner.process_message(message)
        dice = random.randint(1, 6)
        if dice > 4:
            message = Message('ATTACK', 2)
            logging.info(f'{skill.name} 发动 额外造成 2 点伤害')
            skill.owner.process_message(message)


    skill_ysk4 = Skill('欲灵「贪分欲吞噬者」', 4, skill_ysk_4)


    def skill_ysk_5(skill: Skill):
        """
        造成2点伤害 50%概率重复本技能
        """
        while True:
            message = Message('ATTACK', 2)
            logging.info(f'{skill.name} 发动 造成 2 点伤害')
            skill.owner.process_message(message)
            dice = random.randint(1, 6)
            if dice > 3:
                break


    skill_ysk5 = Skill('毒爪「不死杀人鬼」', 5, skill_ysk_5)


    def skill_ysk_6(skill: Skill):
        """
        获得被动技能 涌现 持续1回合 造成伤害与恢复+1
        额外再抽一张牌
        """

        def skill_ysk_6_passive_1(passive: Passive, message: Message):
            if message.kind == 'ATTACK' or message.kind == 'HEALING':
                message.value += 1
                logging.info(f'{skill.name} {passive.name}发动 {message.kind}+1')

        passive = Passive('灵感passive1涌现', 1, skill_ysk_6_passive_1)
        passive.owner = skill.owner
        skill.owner.passives.append(passive)
        skill.owner.skill_stage()


    skill_ysk6 = Skill('灵感', 6, skill_ysk_6)


    def skill_ysk_item_1(passive: Passive, message: Message):
        """
        血量第一次到达5或5以下的伤害结算前 获得涌现 立即抽一张牌并使用
        """
        if message.kind == 'DAMAGE' and not passive.is_expired:
            if 0 < passive.owner.hp - message.value <= 5:
                logging.info(f'{passive.owner.name} 发动道具 {passive.name}')

                def skill_ysk_item_1_passive_1(passive_inner: Passive, message: Message):
                    if message.kind == 'ATTACK' or message.kind == 'HEALING':
                        message.value += 1
                        logging.info(f'{passive.name} {passive_inner.name}发动 {message.kind}+1')

                passive_inner = Passive('道具passive1涌现', 999, skill_ysk_item_1_passive_1)
                passive_inner.owner = passive.owner
                passive.owner.passives.append(passive_inner)
                passive.owner.skill_stage()
                passive.is_expired = True


    item_ysk1 = Passive('邪仙的咒缚', 999, skill_ysk_item_1)

    random.seed(i)

    haruka = Character('晴夏', 1, 15)
    haruka.skills = [skill_hrk1, skill_hrk2, skill_hrk3, skill_hrk4, skill_hrk5, skill_hrk6]
    yoshika = Character('芳香', 5, 15)
    yoshika.skills = [skill_ysk1, skill_ysk2, skill_ysk3, skill_ysk4, skill_ysk5, skill_ysk6]
    yoshika.passives = [item_ysk1]

    game = Game(haruka, yoshika)
    game.start()


    result[game.winner] += 1

print(result)
